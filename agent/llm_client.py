import logging
import tiktoken

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

MODEL_NAME = "gpt-4o"
INPUT_TOKEN_LIMIT = 5000
TEMPERATURE = 0.3


class LLMClient:
    def __init__(self, api_key: str):
        self.model_name = MODEL_NAME
        self.llm = ChatOpenAI(model=MODEL_NAME, temperature=TEMPERATURE, api_key=api_key)

    def invoke(self, prompt: str) -> str:
        """
        Invokes LLM with prompt
        :param prompt: prompt for LLM
        :return: LLM response
        """
        self._validate_token_count(prompt)

        logger.info(f"Invoke LLM {self.model_name}")
        return self.llm.invoke([HumanMessage(content=prompt)]).content

    def _validate_token_count(self, prompt: str) -> None:
        """
        Validates number of tokens
        :param prompt: LLM prompt
        :raise Exception when prompt exceeds token limit
        """
        token_count = self._count_tokens(text=prompt, model_name=MODEL_NAME)
        logger.info(f"Number of tokens: {token_count}")

        if token_count > INPUT_TOKEN_LIMIT:
            logger.info(f"Prompt exceeds token limit: {token_count}")
            raise Exception("Prompt exceeds token limit")

    def _count_tokens(self, text: str, model_name: str) -> int:
        """
        Counts token in text
        :param text: LLM prompt
        :param model_name: LLM model name
        :return: number of tokens
        """
        encoding = tiktoken.encoding_for_model(model_name)
        return len(encoding.encode(text))
