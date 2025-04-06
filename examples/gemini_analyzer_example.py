import os
from scraipe.extended.llm_analyzers import GeminiAnalyzer
from pydantic import BaseModel
# Load API key from environment variable
# Set this in bash using `export GEMINI_API_KEY=example-key`
gemini_key = os.getenv("GEMINI_API_KEY")

# Craft an instruction for the analyzer that specifies the information
# you want to extract and the JSON schema to format the output as
instruction = """
Determine the article's topic and whether the sentiment is positive, negative, or neutral.
Output the result in the following JSON format:
{
    "topic": "<topic>",
    "sentiment": "<positive|negative|neutral>",
}
"""
# Define a pydantic schema for the expected output
class ExpectedOutput(BaseModel):
    topic: str
    sentiment: str
# Initialize the analyzer with the API key, instruction, and schema
analyzer = GeminiAnalyzer(
    api_key=gemini_key,
    instruction=instruction,
    pydantic_schema=ExpectedOutput,
)

# Analyze an article
article = """
Scraipe is a powerful tool for scraping and analyzing web data. It allows users to extract information from websites easily and efficiently.
With Scraipe, users can automate the process of data collection and analysis, saving time and effort.
"""
result = analyzer.analyze(article)
# Output the analysis result
print(result.output)