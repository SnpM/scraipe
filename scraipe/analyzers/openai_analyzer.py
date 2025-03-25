from scraipe.classes import IAnalyzer, AnalysisResult
from openai import OpenAI
import json
from pydantic import BaseModel, ValidationError
from typing import Type

class OpenAiAnalyzer(IAnalyzer):
    """An analyzer that uses the OpenAI API to analyze text and returns a json parsed dict"""
    
    # Attributes
    client:OpenAI
    """The OpenAI instance to use for querying the OpenAI API"""
    instruction:str
    """The instruction or prompt to guide the OpenAI model's behavior"""
    pydantic_schema:Type[BaseModel]
    """A Pydantic schema to validate the model's output"""
    model:str
    """The name of the OpenAI model to use"""
    
    def __init__(self,
        api_key:str,
        instruction:str,
        organization:str=None,
        pydantic_schema:Type[BaseModel] = None,
        model:str="gpt-4o-mini"):
        """Initializes the OpenAIAnalyzer instance."""
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key,organization=organization)
        self.instruction = instruction
        self.pydantic_schema = pydantic_schema
        self.model = model
    
    def query_openai(self, content:str) -> str:
        """Queries the OpenAI API with the content and configured instruction."""
        # Send the content with the instruction as a system instruction
        messages=[
            {"role": "system", "content": self.instruction},
            {"role": "user", "content": content}
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={ "type": "json_object" }
        )
        response_content:str = response.choices[0].message.content
        return response_content

    def analyze(self, content:str) -> AnalysisResult:
        """Analyzes the content using the OpenAI API and returns the response as a dict."""
        try:
            response = self.query_openai(content)
        except Exception as e:
            return AnalysisResult(output=None, success=False, error=f"Failed to query OpenAI: {e}")
        
        # Check if response is json string
        try:
            response_dict = json.loads(response)
        except json.JSONDecodeError:
            return AnalysisResult(success=False, error=f"OpenAI response is not a valid json string: {response}")
        
        # Check if response follows the pydantic schema
        if self.pydantic_schema:
            try:
                self.pydantic_schema(**response_dict)
            except ValidationError as e:
                return AnalysisResult(output=response_dict, success=False, error=f"OpenAI response does not follow the pydantic schema: {e}")
        
        return AnalysisResult(output=response_dict, success=True)