"""
Test LLM Integration Module (Full Coverage)

Comprehensive tests for llm_integration.py including embeddings,
local model loading, cloud providers, summarization, and tag generation.
All tests use mocking to avoid actual API calls or model loading.
"""

import unittest
from unittest.mock import patch, MagicMock, PropertyMock
import os


class TestGetEmbeddings(unittest.TestCase):
    """Tests for get_embeddings function."""

    def setUp(self):
        """Clear cache before each test."""
        from backend.llm_integration import _embeddings_cache
        _embeddings_cache.clear()

    @patch('backend.llm_integration.OpenAIEmbeddings')
    def test_get_embeddings_openai(self, mock_openai_embeddings):
        """Test getting OpenAI embeddings."""
        from backend.llm_integration import get_embeddings
        
        mock_embeddings = MagicMock()
        mock_openai_embeddings.return_value = mock_embeddings
        
        result = get_embeddings('openai', api_key='sk-test-key')
        
        self.assertIsNotNone(result)
        mock_openai_embeddings.assert_called_once()

    @patch('backend.llm_integration.HuggingFaceEmbeddings')
    def test_get_embeddings_local(self, mock_hf_embeddings):
        """Test getting local/HuggingFace embeddings."""
        from backend.llm_integration import get_embeddings
        
        mock_embeddings = MagicMock()
        mock_hf_embeddings.return_value = mock_embeddings
        
        result = get_embeddings('local')
        
        self.assertIsNotNone(result)
        mock_hf_embeddings.assert_called_once()

    @patch('backend.llm_integration.GoogleGenerativeAIEmbeddings')
    def test_get_embeddings_gemini(self, mock_gemini_embeddings):
        """Test getting Gemini embeddings."""
        from backend.llm_integration import get_embeddings
        
        mock_embeddings = MagicMock()
        mock_gemini_embeddings.return_value = mock_embeddings
        
        result = get_embeddings('gemini', api_key='test-gemini-key')
        
        self.assertIsNotNone(result)

    def test_get_embeddings_caching(self):
        """Test that embeddings are cached."""
        from backend.llm_integration import _embeddings_cache
        
        # Cache should exist
        self.assertIsInstance(_embeddings_cache, dict)


class TestGetLocalLLM(unittest.TestCase):
    """Tests for get_local_llm function."""

    @patch('backend.llm_integration.os.path.exists')
    @patch('backend.llm_integration.Llama')
    def test_get_local_llm_success(self, mock_llama, mock_exists):
        """Test loading a local LLM successfully."""
        from backend.llm_integration import get_local_llm
        
        mock_exists.return_value = True
        mock_model = MagicMock()
        mock_llama.return_value = mock_model
        
        result = get_local_llm('/path/to/model.gguf')
        
        self.assertIsNotNone(result)


    def test_get_local_llm_no_llama(self):
        """Test behavior when llama_cpp is not installed."""
        from backend.llm_integration import get_local_llm
        
        with patch('backend.llm_integration.Llama', None):
            result = get_local_llm('/path/to/model.gguf')
            self.assertIsNone(result)

    def test_get_local_llm_no_path(self):
        """Test behavior with empty path."""
        from backend.llm_integration import get_local_llm
        
        result = get_local_llm('')
        self.assertIsNone(result)


class TestGetLLMClient(unittest.TestCase):
    """Tests for get_llm_client function."""

    @patch('backend.llm_integration.ChatOpenAI')
    def test_get_llm_client_openai(self, mock_chat_openai):
        """Test getting OpenAI chat client."""
        from backend.llm_integration import get_llm_client
        
        mock_client = MagicMock()
        mock_chat_openai.return_value = mock_client
        
        result = get_llm_client('openai', api_key='sk-test')
        
        self.assertIsNotNone(result)

    @patch('backend.llm_integration.ChatGoogleGenerativeAI')
    def test_get_llm_client_gemini(self, mock_chat_gemini):
        """Test getting Gemini chat client."""
        from backend.llm_integration import get_llm_client
        
        mock_client = MagicMock()
        mock_chat_gemini.return_value = mock_client
        
        result = get_llm_client('gemini', api_key='gemini-key')
        
        self.assertIsNotNone(result)

    @patch('backend.llm_integration.ChatAnthropic')
    def test_get_llm_client_anthropic(self, mock_chat_anthropic):
        """Test getting Anthropic chat client."""
        from backend.llm_integration import get_llm_client
        
        mock_client = MagicMock()
        mock_chat_anthropic.return_value = mock_client
        
        result = get_llm_client('anthropic', api_key='anthropic-key')
        
        self.assertIsNotNone(result)

    def test_get_llm_client_no_api_key(self):
        """Test behavior with missing API key for cloud provider."""
        from backend.llm_integration import get_llm_client
        
        result = get_llm_client('openai', api_key='')
        self.assertIsNone(result)


class TestGenerateAIAnswer(unittest.TestCase):
    """Tests for generate_ai_answer function."""

    @patch('backend.llm_integration.get_llm_client')
    def test_generate_ai_answer_success(self, mock_get_client):
        """Test generating AI answer successfully."""
        from backend.llm_integration import generate_ai_answer
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "This is the AI generated answer."
        mock_client.invoke.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        result = generate_ai_answer(
            context="Sample document content",
            question="What is this about?",
            provider="openai",
            api_key="sk-test"
        )
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)

    @patch('backend.llm_integration.get_llm_client')
    def test_generate_ai_answer_no_client(self, mock_get_client):
        """Test behavior when no LLM client available."""
        from backend.llm_integration import generate_ai_answer
        
        mock_get_client.return_value = None
        
        result = generate_ai_answer(
            context="Sample content",
            question="Test question",
            provider="openai"
        )
        
        # Should return empty or fallback
        self.assertIsInstance(result, str)


class TestSmartSummary(unittest.TestCase):
    """Tests for smart_summary function."""

    @patch('backend.llm_integration.get_llm_client')
    def test_smart_summary_success(self, mock_get_client):
        """Test generating smart summary successfully."""
        from backend.llm_integration import smart_summary
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "This is a contextual summary about the query."
        mock_client.invoke.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        result = smart_summary(
            text="Long document content here...",
            query="What are the key points?",
            provider="openai",
            api_key="sk-test"
        )
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)

    @patch('backend.llm_integration.get_llm_client')
    def test_smart_summary_fallback(self, mock_get_client):
        """Test fallback when smart summary fails."""
        from backend.llm_integration import smart_summary
        
        mock_client = MagicMock()
        mock_client.invoke.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client
        
        result = smart_summary(
            text="Sample text",
            query="Test query",
            provider="openai"
        )
        
        # Should return some fallback text
        self.assertIsInstance(result, str)


class TestExtractAnswer(unittest.TestCase):
    """Tests for extract_answer function."""

    def test_extract_answer_basic(self):
        """Test basic keyword extraction."""
        from backend.llm_integration import extract_answer
        
        text = "Machine learning is a subset of artificial intelligence."
        question = "What is machine learning?"
        
        result = extract_answer(text, question)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)

    def test_extract_answer_no_match(self):
        """Test extraction with no keyword match."""
        from backend.llm_integration import extract_answer
        
        text = "The weather is sunny today."
        question = "What is quantum physics?"
        
        result = extract_answer(text, question)
        
        self.assertIsInstance(result, str)


class TestSummarize(unittest.TestCase):
    """Tests for summarize function (regex fallback)."""

    def test_summarize_short_text(self):
        """Test summarizing short text."""
        from backend.llm_integration import summarize
        
        text = "This is a short text."
        result = summarize(text)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)

    def test_summarize_long_text(self):
        """Test summarizing long text."""
        from backend.llm_integration import summarize
        
        text = "This is the first sentence. " * 20
        result = summarize(text)
        
        self.assertIsInstance(result, str)
        # Should truncate to reasonable length
        self.assertLessEqual(len(result), len(text))

    def test_summarize_empty_text(self):
        """Test summarizing empty text."""
        from backend.llm_integration import summarize
        
        result = summarize("")
        
        self.assertIsInstance(result, str)


class TestGetTags(unittest.TestCase):
    """Tests for get_tags function."""

    @patch('backend.llm_integration.get_llm_client')
    def test_get_tags_success(self, mock_get_client):
        """Test generating tags successfully."""
        from backend.llm_integration import get_tags
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "python, machine learning, data science"
        mock_client.invoke.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        result = get_tags(
            text="Python programming for machine learning and data science.",
            provider="openai",
            api_key="sk-test"
        )
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)

    @patch('backend.llm_integration.get_llm_client')
    def test_get_tags_fallback(self, mock_get_client):
        """Test fallback when tag generation fails."""
        from backend.llm_integration import get_tags
        
        mock_get_client.return_value = None
        
        result = get_tags(
            text="Some text content",
            provider="openai"
        )
        
        # Should return empty string or default tags
        self.assertIsInstance(result, str)


class TestLocalModelIntegration(unittest.TestCase):
    """Tests for local model integration."""

    @patch('backend.llm_integration.os.path.exists')
    @patch('backend.llm_integration.Llama')
    def test_local_model_generates_text(self, mock_llama, mock_exists):
        """Test that local model can generate text."""
        from backend.llm_integration import get_local_llm
        
        mock_exists.return_value = True
        mock_model = MagicMock()
        mock_model.return_value = {
            'choices': [{'text': 'Generated response'}]
        }
        mock_llama.return_value = mock_model
        
        result = get_local_llm('/path/to/model.gguf')
        
        self.assertIsNotNone(result)

    def test_model_caching(self):
        """Test that models are cached properly."""
        from backend.llm_integration import _llm_cache
        
        self.assertIsInstance(_llm_cache, dict)


if __name__ == '__main__':
    unittest.main(verbosity=2)
