import re
import asyncio
from typing import List, Dict, Any, Generator
from backend import tools, llm_integration
import concurrent.futures

class ReActAgent:
    def __init__(self, global_state: dict):
        self.global_state = global_state
        self.max_steps = 5
        self.history = []
        
        # Configure LLM
        config = global_state['config']
        self.provider = config.get('LocalLLM', 'provider', fallback='openai')
        self.api_key = config.get('APIKeys', f"{self.provider}_api_key", fallback='')
        self.model_path = config.get('LocalLLM', 'model_path', fallback='')

    async def stream_chat(self, user_query: str) -> Generator[Dict[str, str], None, None]:
        """
        Runs the ReAct loop and streams events (thoughts, actions, answer).
        Yields dicts like: {"type": "thought", "content": "..."}
        """
        
        system_prompt = """You are an advanced Research Assistant. Answer the user's question by thinking step-by-step and using tools.
        
AVAILABLE TOOLS:
- search_knowledge_base(query): Search the indexed documents for concepts, people, and data.
- list_files(): List the names of all indexed files.
- read_file(filename_or_path): Read the full text content of a specific file.

STRICT FORMAT:
Thought: (Explain what you are looking for and why)
Action: (Exactly one of: search_knowledge_base, list_files, read_file)
Action Input: (The parameter for the tool)

Wait for the "Observation:" from the system before continuing. 
When you have the final answer, use this format:
Final Answer: (Your detailed response citing sources)

CRITICAL: 
- If searching for a person, use their exact name.
- If you find a relevant file in search, use 'read_file' to get details.
- Do NOT hallucinate info not in the documents.
"""

        history = [f"Question: {user_query}"]
        
        for step in range(self.max_steps):
            # Construct Prompt
            prompt = system_prompt + "\n\n" + "\n".join(history) + "\n\nThought:"
            
            # Generate LLM response
            # We use a custom generation wrapper that just completes text
            # We shouldn't use 'generate_ai_answer' because it wraps the prompt.
            # We need a direct completion.
            # hack: use smart_summary's client access or specific method.
            # Re-using llm_integration.generate_ai_answer with a "raw" flag would be ideal.
            # For now, let's reuse generate_ai_answer but pass the whole prompt as 'context' and empty 'question'? 
            # No, prompt injection issues.
            # Better: calling client directly.
            
            client = llm_integration.get_llm_client(self.provider, self.api_key, self.model_path)
            
            response_text = ""
            try:
                if isinstance(client, str) and client.startswith("LOCAL:"):
                    # Local Llama
                    llm = llm_integration.get_local_llm(client.split("LOCAL:")[1])
                    output = llm.create_completion(
                        prompt, 
                        max_tokens=256, 
                        stop=["Observation:", "Definition:", "Thought:"], 
                        echo=False,
                        temperature=0.1,
                        repeat_penalty=1.1
                    )
                    response_text = output['choices'][0]['text']
                else:
                    # LangChain
                    from langchain_core.messages import HumanMessage, SystemMessage
                    # LangChain chat models expect messages
                    # We send one big human message for the ReAct state?
                    # Or System + Human chain.
                    msgs = [
                       SystemMessage(content=system_prompt),
                       HumanMessage(content="\n".join(history) + "\n\nThought:")
                    ]
                    resp = client.invoke(msgs)
                    response_text = resp.content
            except Exception as e:
                yield {"type": "error", "content": f"LLM Error: {e}"}
                return

            # Clean response
            response_text = response_text.strip()
            
            # Print for server console debug
            print(f"\n[AGENT THOUGHT] {response_text}\n")
            
            # Parse Thought/Action from response
            # Sometimes LLM outputs "Thought: x \n Action: y" 
            # Sometimes we provided "Thought:" prefix so it outputs "x \n Action: y"
            
            # We appended "Thought:" to prompt, so response is just the rest.
            current_step_log = f"Thought: {response_text}"
            history.append(current_step_log)
            
            # Extract Action using primary format
            action_match = re.search(r"Action:\s*(search_knowledge_base|list_files|read_file)", response_text, re.IGNORECASE)
            input_match = re.search(r"Action Input:\s*(.+)", response_text, re.IGNORECASE | re.DOTALL)
            
            # Fallback for tool-call style: search_knowledge_base("input")
            if not action_match or not input_match:
                fallback_match = re.search(r"(search_knowledge_base|list_files|read_file)\s*\((\"|')?(.*?)(\"|')?\)", response_text, re.IGNORECASE)
                if fallback_match:
                    action_name = fallback_match.group(1).lower()
                    action_input = fallback_match.group(3)
                    # Create artificial matches for the logic below
                    class MockMatch:
                        def __init__(self, val): self.val = val
                        def group(self, _): return self.val
                    action_match = MockMatch(action_name)
                    input_match = MockMatch(action_input)

            if "Final Answer:" in response_text:
                final_ans = response_text.split("Final Answer:")[-1].strip()
                print(f"[AGENT FINAL ANSWER] {final_ans}")
                yield {"type": "answer", "content": final_ans}
                return
            
            if not action_match or not input_match:
                # Provide feedback to the agent if they tried to call a tool but failed format
                if "Action:" in response_text or "(" in response_text:
                    err_msg = "Error: Invalid format. Please use 'Action: [tool_name]' and 'Action Input: [input]' strictly."
                    print(f"[AGENT CORRECTION] {err_msg}")
                    history.append(f"Observation: {err_msg}")
                    yield {"type": "error", "content": f"Agent Error: Malformed action. Sending correction to AI..."}
                    continue
                else:
                    # If it just thought without action, nudge it
                    if len(response_text) > 40:
                        thought_content = response_text
                        yield {"type": "thought", "content": thought_content}
                        # If it seems like an answer, treat it as one
                        if "Final Answer:" not in response_text and step > 1:
                             print(f"[AGENT AUTO-ANSWER] {response_text}")
                             yield {"type": "answer", "content": response_text}
                             return
                    
                    err_msg = "Observation: You provided a thought but no Action. Please choose a tool to proceed or provide a 'Final Answer:'."
                    history.append(err_msg)
                    continue

            action = action_match.group(1).strip().lower()
            action_input = input_match.group(1).strip()
            
            print(f"[AGENT ACTION] {action}('{action_input}')")
            yield {"type": "thought", "content": f"Decided to use {action} on '{action_input}'"}
            yield {"type": "action", "content": f"Executing {action}..."}
            
            # Execute Tool
            tool_func = tools.AVAILABLE_TOOLS.get(action)
            observation = ""
            if tool_func:
                try:
                    if action == "search_knowledge_base":
                        observation = tool_func(action_input, self.global_state)
                    else:
                        observation = tool_func(action_input)
                except Exception as e:
                    observation = f"Error executing tool {action}: {e}"
            else:
                observation = f"Error: Tool '{action}' not found. Available: {list(tools.AVAILABLE_TOOLS.keys())}"
                
            print(f"[AGENT OBSERVATION] {observation[:200]}...")
            history.append(f"Observation: {observation}")
            yield {"type": "observation", "content": observation[:200] + "..."}
            
        print("[AGENT ERROR] Max steps reached.")
        yield {"type": "error", "content": "The agent was unable to find a definitive answer within the allotted steps."}
