from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import Type
from scraipe.extended.llm_analyzers.llm_analyzer_base import LlmAnalyzerBase

class OpenAiAnalyzer(LlmAnalyzerBase):
    """An LlmAnalyzer that uses the OpenAI API."""

    def __init__(self,
        api_key:str,
        instruction:str,
        organization:str=None,
        pydantic_schema:Type[BaseModel] = None,
        model:str="gpt-4o-mini",
        max_content_size:int=10000,
        max_workers:int=3):
        """Initializes the OpenAIAnalyzer instance.
        
        Args:
            api_key (str): The API key for OpenAI.
            instruction (str): The instruction to be used for the LLM.
            organization (str, optional): The organization to be used for the OpenAI API. Defaults to None.
            pydantic_schema (Type[BaseModel], optional): The pydantic schema to be used for validating the response. Defaults to None.
            model (str, optional): The model to be used for the OpenAI API. Defaults to "gpt-4o-mini".
            max_content_size (int, optional): The maximum size of the content to be analyzed. Defaults to 10000.
            max_workers (int, optional): The maximum number of workers to be used for the analysis. Defaults to 3.
        """
        super().__init__(
            instruction=instruction, pydantic_schema=pydantic_schema,
            max_content_size=max_content_size,max_workers=max_workers)
        self.api_key = api_key
        self.client = AsyncOpenAI(api_key=api_key,organization=organization)
        self.model = model
    
    async def query_llm(self, content:str, instruction:str) -> str:
        """Queries the OpenAI API with the content and configured instruction."""        
        # Send the content with the instruction as a system instruction
        messages=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": content}
        ]
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={ "type": "json_object" }
        )
        # Extract the content from the response
        response_content:str = response.choices[0].message.content
        return response_content