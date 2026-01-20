from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_huggingface import HuggingFaceEmbeddings
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None
import re
import os

# Cache for loaded models
_embeddings_cache = {}
_llm_cache = {}
_llm_client_cache = {}

def get_embeddings(provider, api_key=None, model_path=None):
    """Returns an embeddings model instance based on the provider."""
    cache_key = f"{provider}:{api_key or ''}"
    
    if cache_key in _embeddings_cache:
        return _embeddings_cache[cache_key]
    
    print(f"Loading embeddings for provider: {provider}")

    if provider == 'openai' and api_key:
        embeddings = OpenAIEmbeddings(api_key=api_key)
    elif provider == 'gemini' and api_key:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
    elif provider == 'grok' and api_key:
        # Grok typically uses OpenAI compatible API, but for embeddings they might not have a dedicated endpoint yet
        # or it might be compatible. For safety, we can fallback to local or OpenAI if specified.
        # Assuming Grok users might want local embeddings to save cost/latency if not specified otherwise.
        # But actually, let's just use HuggingFace local for everything else to keep it simple and free.
        # Unless user specifically wants cloud embeddings.
        print("Using local embeddings for Grok provider.")
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    else:
        # Default / Local
        print("Loading local embeddings (HuggingFace)...")
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    
    print("Embeddings loaded!")
    _embeddings_cache[cache_key] = embeddings
    return embeddings

def get_local_llm(model_path):
    """Load and cache the GGUF model directly with LlamaCpp."""
    if not Llama:
        print("llama_cpp not installed")
        return None
        
    if not model_path or not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        return None

    if model_path in _llm_cache:
        return _llm_cache[model_path]

    print(f"Loading Local LLM from {model_path}...")
    try:
        # Load with reasonable defaults for CPU inference
        llm = Llama(
            model_path=model_path,
            n_ctx=4096,  # Larger context window
            n_threads=4, # cpu threads
            verbose=False
        )
        _llm_cache[model_path] = llm
        print("Local LLM loaded!")
        return llm
    except Exception as e:
        print(f"Failed to load Local LLM: {e}")
        return None

def get_llm_client(provider, api_key=None, model_path=None):
    """
    Returns a LangChain-compatible Chat Model or None if configuration is invalid.
    """
    cache_key = f"{provider}:{api_key or ''}:{model_path or ''}"
    if cache_key in _llm_client_cache:
        return _llm_client_cache[cache_key]

    client = None
    try:
        if provider == 'openai':
            if not api_key:
                print("OpenAI API Key missing")
                return None
            client = ChatOpenAI(api_key=api_key, model="gpt-4o-mini", temperature=0.3)

        elif provider == 'gemini':
            if not api_key:
                print("Gemini API Key missing")
                return None
            client = ChatGoogleGenerativeAI(google_api_key=api_key, model="gemini-1.5-flash", temperature=0.3)

        elif provider == 'anthropic':
            if not api_key:
                print("Anthropic API Key missing")
                return None
            client = ChatAnthropic(api_key=api_key, model="claude-3-haiku-20240307", temperature=0.3)

        elif provider == 'grok':
            if not api_key:
                print("Grok API Key missing")
                return None
            # Grok uses OpenAI-compatible endpoint
            client = ChatOpenAI(
                api_key=api_key,
                base_url="https://api.x.ai/v1",
                model="grok-beta",
                temperature=0.3
            )

        elif provider == 'local':
            # For local, we don't return a LangChain object because we are using llama-cpp-python directly
            # for better control over the 'create_completion' call in generate_ai_answer currently.
            # However, for 'smart_summary', we might want a unified interface.
            # For now, return a special marker or the model path wrapper?
            # Let's return the model_path string, and handle it in the consumer.
            if not model_path or not os.path.exists(model_path):
                print("Local model path missing or invalid")
                return None
            client = "LOCAL:" + model_path

    except Exception as e:
        print(f"Error initializing LLM client for {provider}: {e}")
        return None

    if client:
        _llm_client_cache[cache_key] = client
    return client

def generate_ai_answer(context, question, provider, api_key=None, model_path=None):
    """
    Generate a natural language answer using the selected provider.
    """
    # Get client
    client = get_llm_client(provider, api_key, model_path)
    if not client:
        return "Error: Could not initialize AI model. Check settings and API keys."

    prompt_text = f"""You are a document search assistant. Answer the question using ONLY facts from the provided documents.

IMPORTANT: Quote specific content, data, numbers, or key details from the documents. Reference which file the information comes from when possible. Don't give generic answers.

Documents:
{context}

Question: {question}

Answer (cite specific details from the documents):"""

    try:
        # Handle Local LLM (LlamaCpp)
        if isinstance(client, str) and client.startswith("LOCAL:"):
            real_model_path = client.split("LOCAL:")[1]
            llm = get_local_llm(real_model_path)
            if not llm:
                return "Error: Local model failed to load."

            output = llm.create_completion(
                prompt_text,
                max_tokens=512,
                stop=["System:", "Question:", "Context:"],
                echo=False,
                temperature=0.3
            )
            return output['choices'][0]['text'].strip()

        # Handle LangChain Clients (Cloud)
        else:
            from langchain_core.messages import HumanMessage, SystemMessage

            messages = [
                SystemMessage(content="You are a document search assistant. Quote specific content, data, numbers, or details from the documents. Reference file names when available."),
                HumanMessage(content=f"Documents:\n{context}\n\nQuestion: {question}\n\nAnswer with specific details:")
            ]

            response = client.invoke(messages)
            return response.content.strip()

    except Exception as e:
        print(f"Generation error ({provider}): {e}")
        return f"Error generating answer: {str(e)}"

def smart_summary(text, query, provider, api_key=None, model_path=None, file_name=None):
    """
    Generates a contextual summary of the text specifically related to the query.
    Optionally includes file_name for better context in the response.
    """
    if not text:
        return ""

    client = get_llm_client(provider, api_key, model_path)
    if not client:
        # Fallback to regex summary if no model available
        return summarize(text, provider, api_key, model_path, query)

    # Truncate text to avoid token limits (approx 3000 chars ~ 750 tokens)
    truncated_text = text[:3000]
    
    file_context = f" from '{file_name}'" if file_name else ""

    prompt_text = f"""Analyze this document excerpt{file_context} for the query: "{query}".

Extract and quote specific facts, data, or content that answers the query. Be specific - include numbers, names, dates, or key details from the document.

If irrelevant, say "No relevant info".

Document:
{truncated_text}

Key findings:"""

    try:
        # Handle Local LLM
        if isinstance(client, str) and client.startswith("LOCAL:"):
            real_model_path = client.split("LOCAL:")[1]
            llm = get_local_llm(real_model_path)
            if not llm:
                return summarize(text, provider, api_key, model_path, query)

            output = llm.create_completion(
                prompt_text,
                max_tokens=128,
                stop=["Document Excerpt:", "Summary:"],
                echo=False,
                temperature=0.1
            )
            result = output['choices'][0]['text'].strip()

        # Handle LangChain Clients
        else:
            from langchain_core.messages import HumanMessage
            response = client.invoke([HumanMessage(content=prompt_text)])
            result = response.content.strip()

        if "No relevant info" in result or len(result) < 5:
            return summarize(text, provider, api_key, model_path, query) # Fallback

        return result

    except Exception as e:
        print(f"Smart summary error: {e}")
        return summarize(text, provider, api_key, model_path, query) # Fallback

def extract_answer(text, question):
    """
    Legacy extraction: keyword matching fallback.
    """
    if not text or not question:
        return None
    
    question_lower = question.lower()
    cleaned_q = re.sub(r'\b(what|where|when|who|why|how|which|did|does|is|are|was|were)\b', '', question_lower)
    question_terms = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', cleaned_q) if w not in {'the', 'and', 'for', 'that', 'this'}]
    
    if not question_terms:
        return None
    
    sentences = re.split(r'(?<=[.!?])\s+', text)
    scored_sentences = []
    for sent in sentences:
        sent_lower = sent.lower()
        score = sum(1 for term in question_terms if term in sent_lower)
        if score > 0:
            scored_sentences.append((score, sent))
    
    scored_sentences.sort(reverse=True, key=lambda x: x[0])
    
    if scored_sentences:
        best_sentences = [s[1].strip() for s in scored_sentences[:2]]
        answer = ' '.join(best_sentences)
        if len(answer) > 300:
            answer = answer[:297] + "..."
        return answer
    
    return None

def summarize(text, provider=None, api_key=None, model_path=None, question=None):
    """
    Fast regex-based summary (fallback).
    """
    try:
        if question:
            answer = extract_answer(text, question)
            if answer:
                return answer
        
        text = re.sub(r'\s+', ' ', text).strip()
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        summary_sentences = []
        for sent in sentences:
            if len(sent) > 30:
                summary_sentences.append(sent)
                if len(summary_sentences) >= 2:
                    break
        
        if summary_sentences:
            return ' '.join(summary_sentences)
        return text[:150] + "..." if len(text) > 150 else text
    except Exception as e:
        print(f"Error: {e}")
        return ""

def get_tags(text, provider, api_key=None, model_path=None):
    try:
        words = re.findall(r'\b[a-zA-Z]{4,15}\b', text.lower())
        stop_words = {
            'this', 'that', 'with', 'from', 'have', 'will', 'been', 'would',
            'could', 'should', 'their', 'there', 'about', 'which', 'these',
            'other', 'more', 'some', 'such', 'only', 'than', 'into', 'over'
        }
        words = [w for w in words if w not in stop_words]
        word_freq = {}
        for w in words:
            word_freq[w] = word_freq.get(w, 0) + 1
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        return ', '.join([w[0] for w in top_words])
    except Exception as e:
        return ""
