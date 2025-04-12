from typing import Type
import google.genai
import google.genai.errors
from pydantic import BaseModel
from scraipe.extended.llm_analyzers.llm_analyzer_base import LlmAnalyzerBase

from google.genai import Client
from google.genai.types import GenerateContentConfig
import google

class GeminiAnalyzer(LlmAnalyzerBase):
    """An LlmAnalyzer that uses the Gemini API."""

    def __init__(self,
        api_key: str,
        instruction: str,
        pydantic_schema: Type[BaseModel] = None,
        model: str = "gemini-2.0-flash",
        max_content_size: int = 10000,
        max_workers: int = 1):
        """Initializes the GeminiAnalyzer instance.
        
        Args:
            api_key (str): The API key for Gemini.
            instruction (str): The instruction to be used for the LLM.
            pydantic_schema (Type[BaseModel], optional): The pydantic schema to be used for validating the response.
            model (str, optional): The model to be used for the Gemini API. Defaults to "gemini-2.0-flash".
            max_content_size (int, optional): The maximum size of the content to be analyzed. Defaults to 10000 characters.
            max_workers (int, optional): The maximum number of workers to be used for the analysis. Defaults to 1 due to aggressive rate limiting.
        """
        super().__init__(
            instruction=instruction, pydantic_schema=pydantic_schema,
            max_content_size=max_content_size, max_workers=max_workers)
        
        self.model = model
        self.client = Client(api_key=api_key)
        self.api_key = api_key
        
        self.validate()
        
    def validate(self, test_client: Client = None) -> None:
        """Validates the API key and model by attempting to retrieve the model from the Gemini API.
        
        Args:
            test_client (Client, optional): A test client instance for mocking. Defaults to None.
        
        Raises:
            AssertionError: If the model is not found in the Gemini API.
        """
        client = test_client or self.client
        try:
            print(client._api_client.api_key)
            model_instance = client.models.get(model=self.model)
        except google.genai.errors.ClientError as e:
            raise Exception(f"Check your API key.") from e
        
        assert model_instance is not None, f"Model {self.model} not found in Gemini API. Please check your API key and model name."
    
    async def query_llm(self, content: str, instruction: str) -> str:
        """Asynchronously queries the Gemini API with the given content using the configured system instruction.
        
        Args:
            content (str): The textual content to analyze.
            instruction (str): The system instruction to be used by the Gemini API.
        
        Returns:
            str: The generated response content in JSON format.
        """
        config = GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=self.pydantic_schema,
            system_instruction=instruction,
        )
        
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=[content],
            config=config
        )
        
        response_content: str = response.text
        return response_content