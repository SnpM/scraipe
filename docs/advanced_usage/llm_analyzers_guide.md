# LLM Analyzers Guide

LLM analyzers in Scraipe enable advanced parsing of content using large language models. This guide covers the following:

- Overview of built-in LLM analyzers
- How to configure and use them
- Writing a custom LLM analyzer

## Overview

Scraipe provides [`GeminiAnalyzer`][scraipe.extended.llm_analyzers.GeminiAnalyzer] and [`OpenAiAnalyzer`][scraipe.extended.llm_analyzers.GeminiAnalyzer] to leverage the popular LLM providers. These analyzers inherit from a common [`LlmAnalyzerBase`][scraipe.extended.llm_analyzers.LlmAnalyzerBase], a [custom component](./custom_components.md) that handles request orchestration, validation using pydantic schemas, and response processing 

## Using OpenAiAnalyzer

Most LLM analyzers will need to be configured with the following parameters:

- `instruction`: the system instruction to guide the LLM's behavior.
- `api_key`: the API key to access the LLM provider's service.
- `pydantic_schema`: a [Pydantic model](https://docs.pydantic.dev/latest/concepts/models/) that defines the schema for the LLM's JSON response. 

The specific configuration options will depend on the `LlmAnalyzerBase` implementation. Here is an example with `OpenAiAnalyzer`.

1. Import dependencies and API key

    ```python
    import os
    from scraipe.extended.llm_analyzers import OpenAiAnalyzer
    from pydantic import BaseModel

    # Load OpenAI API key from environment variable
    # Set this in bash using `export OPENAI_API_KEY=example-key`
    openai_key = os.getenv("OPENAI_API_KEY")
    ```

2. Configure the analyzer with a prompt and schema
    ```python
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
    # Initialize the OpenAiAnalyzer with the API key, instruction, and schema
    analyzer = OpenAiAnalyzer(
        api_key=openai_key,
        instruction=instruction,
        pydantic_schema=ExpectedOutput,
    )
    ```

3. Analyze and display results
    ```python
    # Analyze an article
    article = """
    Scraipe is a powerful tool for scraping and analyzing web data. It allows users to extract information from websites easily and efficiently.
    With Scraipe, users can automate the process of data collection and analysis, saving time and effort.
    """
    result = analyzer.analyze(article)

    # Output the analysis result
    print(result.output)
    ```

Running [our script]

## Extending LLM Analyzers

To create custom analyzers:

1. Extend `LlmAnalyzerBase`.
2. Implement the `query_llm()` method with your desired LLM integration.
3. Adjust the initialization to accept additional parameters. Ensure `super().__init__()` is called.

Example:

```python
from scraipe.extended.llm_analyzers.llm_analyzer_base import LlmAnalyzerBase

class CustomLlmAnalyzer(LlmAnalyzerBase):
    def __init__(self, api_key: str, instruction: str, pydantic_schema, custom_param: str, **kwargs):
        super().__init__(instruction=instruction, pydantic_schema=pydantic_schema, **kwargs)
        self.api_key = api_key
        self.custom_param = custom_param
        # Initialize your custom client
    
    async def query_llm(self, content: str, instruction: str) -> str:
        # Customize request preparation for your LLM API
        response = "custom response json string"  # Replace with actual API call
        return response
```

## Advanced Usage

- **Error Handling**: Ensure that failures in API calls are caught and wrapped in an `AnalysisResult.fail()` call.
- **Content Size**: The base class automatically chunks content if it exceeds the maximum length.
- **Schema Validation**: Custom analyzers can choose to enforce strict validation rules using pydantic.

## Further Reading

For additional details, see:
- [Custom Components Guide](./custom_components.md) – for extending other Scraipe components.
- [MultiScraper Guide](./multi_scraper_guide.md) – for examples on flexible component integration.

Happy analyzing!