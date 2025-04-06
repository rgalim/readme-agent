import tiktoken
from src.llm.prompt_manager import count_tokens, create_prompt


def test_count_tokens_empty(monkeypatch):
    class MockEncoding:
        def encode(self, text):
            return []

    def mock_encoding_for_model(model_name):
        return MockEncoding()

    monkeypatch.setattr(tiktoken, "encoding_for_model", mock_encoding_for_model)

    assert count_tokens("", "fake-model") == 0


def test_count_tokens_non_empty(monkeypatch):
    class Mockncoding:
        def encode(self, text):
            return text.split()

    def mock_encoding_for_model(model_name):
        return Mockncoding()

    monkeypatch.setattr(tiktoken, "encoding_for_model", mock_encoding_for_model)

    text = "hello world this is a test"
    expected_token_count = len(text.split())
    assert count_tokens(text, "mock-model") == expected_token_count


def test_create_prompt_includes_file_content():
    sample_content = "File1 content\nFile2 content"
    prompt = create_prompt(sample_content)

    assert sample_content in prompt
    assert "The files provided are:" in prompt


def test_create_prompt_with_empty_content():
    prompt = create_prompt("")

    assert "The files provided are:" in prompt
    assert "Generate a well-structured and detailed README file" in prompt
