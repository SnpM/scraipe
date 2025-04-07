from scraipe.classes import IAnalyzer, AnalysisResult
import json
from pydantic import BaseModel, ValidationError
from typing import Type
from abc import abstractmethod
from scraipe.async_classes import IAsyncAnalyzer

class LlmAnalyzerBase(IAsyncAnalyzer):
    """Base class for LLM analyzers. This class should not be used directly.
    This class provides a common interface for LLM analyzers and handles the common logic for analyzing content using LLMs.
    query_llm() is an abstract method that requires the model to return a json string.
    """
    
    # Attributes
    instruction:str
    """The instruction to be used for the LLM. This should be a string that describes the task to be performed."""
    pydantic_schema:Type[BaseModel] = None
    """The pydantic schema to be used for validating the response. This should be a subclass of pydantic.BaseModel."""
    max_content_size:int = 10000
    """The maximum size of the content to be analyzed. This should be an integer that specifies the maximum number of characters."""
    max_workers:int = 3
    """The maximum number of workers to be used for the analysis. This should be an integer that specifies the maximum number of concurrent requests."""
    
    def __init__(self,
        instruction:str,
        pydantic_schema:Type[BaseModel] = None,
        max_content_size:int=10000,
        max_workers:int=3):
        super().__init__(max_workers=max_workers)
        self.instruction = instruction
        self.pydantic_schema = pydantic_schema
        self.max_content_size = max_content_size
    
    
    @abstractmethod
    async def query_llm(self, content: str, instruction: str) -> str:
        """Queries the LLM API with the provided content and instruction.

        Parameters:
            content (str): The content to be analyzed.
            instruction (str): The instruction describing the task for the LLM.

        Returns:
            str: A JSON-formatted string response from the LLM.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    async def async_analyze(self, content: str) -> AnalysisResult:
        """Analyzes the provided content by querying the LLM and validating the response.

        Parameters:
            content (str): The content to be analyzed. It must be a non-empty string. If the content exceeds the maximum allowed size, it will be truncated.

        Returns:
            AnalysisResult: An object indicating the success or failure of the analysis. On success, the output contains the validated response data; on failure, it contains an error message.
        """
        
        # Ensure content is a non-empty string
        if not isinstance(content, str) or len(content) == 0:
            return AnalysisResult.fail("Content is not a valid string.")
        
        # Cap the content size to the max_content_size
        if len(content) > self.max_content_size:
            content = content[:self.max_content_size]
        
        try:
            response = await self.query_llm(content, self.instruction)
        except Exception as e:
            return AnalysisResult.fail(f"Failed to query LLM: {e}")
        
        # Check if response is json string
        try:
            response_dict = json.loads(response)
        except json.JSONDecodeError:
            return AnalysisResult.fail(f"LLM response is not a valid json string: {response}")
        
        # Check if response follows the pydantic schema
        output = response_dict
        if self.pydantic_schema:
            try:
                validated = self.pydantic_schema(**response_dict)
                output = validated.model_dump()
            except ValidationError as e:
                return AnalysisResult.fail(f"OpenAI response does not follow the pydantic schema: {e}")
        
        return AnalysisResult.succeed(output=output)


