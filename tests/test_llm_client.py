import unittest
from unittest.mock import patch, MagicMock
from agent.llm_client import (
    LLMClient,
    MODEL_NAME,
    TEMPERATURE,
    INPUT_TOKEN_LIMIT,
)


class TestLLMClient(unittest.TestCase):
    @patch("agent.llm_client.ChatOpenAI")
    def test_init_sets_model_and_llm(self, mock_chat_openai):
        """Test init client setup"""
        api_key = "api_key"
        client = LLMClient(api_key)

        assert client.model_name == MODEL_NAME

        mock_chat_openai.assert_called_once_with(
            model=MODEL_NAME, temperature=TEMPERATURE, api_key=api_key
        )
        self.assertIs(client.llm, mock_chat_openai.return_value)

    @patch("agent.llm_client.LLMClient._count_tokens", return_value=5)
    @patch("agent.llm_client.ChatOpenAI")
    def test_invoke_success(self, mock_chat_openai, mock_count_tokens):
        """Test successful LLM invoke"""
        prompt = "My prompt"
        client = LLMClient("api_key")
        dummy_response = MagicMock()
        dummy_response.content = "LLM response"
        mock_chat_openai.return_value.invoke.return_value = dummy_response

        result = client.invoke(prompt)

        mock_count_tokens.assert_called_once_with(text=prompt, model_name=MODEL_NAME)

        invoked_args, _ = mock_chat_openai.return_value.invoke.call_args
        msgs = invoked_args[0]

        assert len(msgs) == 1
        assert msgs[0].content == prompt
        assert result == "LLM response"

    @patch("agent.llm_client.LLMClient._count_tokens", return_value=INPUT_TOKEN_LIMIT + 1)
    @patch("agent.llm_client.ChatOpenAI")
    def test_invoke_exceeds_token_limit(self, mock_chat_openai, mock_count_tokens):
        """Test LLM invoke with exceeding token limit"""
        prompt = "x" * 1000
        client = LLMClient("api_key")

        with self.assertRaises(Exception) as cm:
            client.invoke(prompt)
        self.assertEqual(str(cm.exception), "Prompt exceeds token limit")

        mock_chat_openai.return_value.invoke.assert_not_called()

    @patch("agent.llm_client.ChatOpenAI")
    @patch("agent.llm_client.tiktoken.encoding_for_model")
    def test_count_tokens_uses_tiktoken(self, mock_encoding_for_model, mock_chat_openai):
        """Test tokens count with tiktoken"""
        text = "abcde"
        fake_encoding = MagicMock()
        fake_encoding.encode.return_value = list(text)
        mock_encoding_for_model.return_value = fake_encoding

        client = LLMClient("api_key")

        count = client._count_tokens(text, MODEL_NAME)

        mock_encoding_for_model.assert_called_once_with(MODEL_NAME)
        fake_encoding.encode.assert_called_once_with(text)
        assert count == 5

    @patch("agent.llm_client.LLMClient._count_tokens", return_value=INPUT_TOKEN_LIMIT + 10)
    @patch("agent.llm_client.ChatOpenAI")
    def test_validate_token_count_above_limit(self, mock_chat_openai, mock_count_tokens):
        """Test tokens count above limit"""
        client = LLMClient("api_key")
        with self.assertRaises(Exception) as ex:
            client._validate_token_count("dummy")

        assert str(ex.exception) == "Prompt exceeds token limit"
