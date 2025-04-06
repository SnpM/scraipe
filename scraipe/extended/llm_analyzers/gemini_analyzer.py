from typing import Type
from pydantic import BaseModel
from scraipe.extended.llm_analyzers.llm_analyzer_base import LlmAnalyzerBase

from google.genai import Client
from google.genai.types import GenerateContentConfig

class GeminiAnalyzer(LlmAnalyzerBase):
    """An LlmAnalyzer that uses the Gemini API."""

    def __init__(self,
        api_key:str,
        instruction:str,
        pydantic_schema:Type[BaseModel],
        model:str="gemini-2.0-flash",
        max_content_size:int=10000,
        max_workers:int=3):
        """Initializes the GeminiAnalyzer instance.
        
        Args:
            api_key (str): The API key for Gemini.
            instruction (str): The instruction to be used for the LLM.
            pydantic_schema (Type[BaseModel], optional): The pydantic schema to be used for validating the response. Defaults to None.
            model (str, optional): The model to be used for the Gemini API. Defaults to "gemini-2.0-flash".
            max_content_size (int, optional): The maximum size of the content to be analyzed. Defaults to 10000.
            max_workers (int, optional): The maximum number of workers to be used for the analysis. Defaults to 3.
        """
        super().__init__(
            instruction=instruction, pydantic_schema=pydantic_schema,
            max_content_size=max_content_size,max_workers=max_workers)
        
        self.model = model
        self.client = Client(api_key=api_key)
        self.api_key = api_key
    
    async def query_llm(self, content:str, instruction:str) -> str:
        """Queries the Gemini API with the content and configured instruction."""
        # Prepare the prompt with the instruction and content
        
        config = GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=self.pydantic_schema,
            system_instruction=self.instruction,
        )
        
        # Generate content using the Gemini API
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=[content],
            config=config
        )                       
        
        # Extract the content from the response
        response_content:str = response.text
        return response_content