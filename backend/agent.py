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
        
        system_prompt = """You are a research agent. Answer the user's question using the available tools.
        
TOOLS:
- search_knowledge_base(query): Search the document index for information.
- list_files(): List available file names.
- read_file(path): Read the full content of a file.

FORMAT:
1. Thought: Comment on what you need to find.
2. Action: tool_name
3. Action Input: input_string
4. Observation: [Tool output will be inserted here]
... (Repeat)
5. Final Answer: Your detailed response.

IMPORTANT: 
- Use 'search_knowledge_base' first to find relevant files.
- If you find a file but need more details, use 'read_file'.
- If the tool output contains the answer, OUTPUT 'Final Answer:'.
- Do not make up information.
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
                        stop=["Observation:", "Definition:"], 
                        echo=False
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
            full_thought = f"Thought: {response_text}"
            
            # Parse Thought/Action from response
            # Sometimes LLM outputs "Thought: x \n Action: y" 
            # Sometimes we provided "Thought:" prefix so it outputs "x \n Action: y"
            
            # We appended "Thought:" to prompt, so response is just the rest.
            current_step_log = f"Thought: {response_text}"
            history.append(current_step_log)
            
            # Extract Action
            # Regex for "Action: (.+?)\nAction Input: (.+)"
            action_match = re.search(r"Action:\s*(.+?)\nAction Input:\s*(.+)", response_text, re.DOTALL)
            
            if "Final Answer:" in response_text:
                final_ans = response_text.split("Final Answer:")[-1].strip()
                yield {"type": "answer", "content": final_ans}
                return
            
            if not action_match:
                # Maybe it just thought?
                yield {"type": "thought", "content": response_text.split("Action:")[0].strip()}
                if "Action:" in response_text:
                    # Malformed action
                    pass
                else:
                     # If it stopped without action, maybe it's done or confused?
                     # Force it to final answer if it looks like an answer?
                     if len(response_text) > 50:
                         yield {"type": "answer", "content": response_text}
                         return
                     continue

            action = action_match.group(1).strip()
            action_input = action_match.group(2).strip()
            
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
                    observation = f"Error: {e}"
            else:
                observation = f"Error: Tool '{action}' not found."
                
            obs_log = f"Observation: {observation[:500]}..." # Log short
            history.append(f"Observation: {observation}")
            
            yield {"type": "observation", "content": observation[:200] + "..."}
            
        yield {"type": "error", "content": "Max steps reached without final answer."}
