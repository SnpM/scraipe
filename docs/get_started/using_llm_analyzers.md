# Using LLM Analyzers

LLM analyzers provide intelligent feature extraction with large language models. This page covers how to configure and use LLM analyzers provided by Scraipe.

## Overview

Scraipe provides [`GeminiAnalyzer`][scraipe.extended.llm_analyzers.GeminiAnalyzer] and [`OpenAiAnalyzer`][scraipe.extended.llm_analyzers.GeminiAnalyzer] to leverage these popular cloud-based providers. These analyzers extend [`LlmAnalyzerBase`][scraipe.extended.llm_analyzers.LlmAnalyzerBase], a custom component that handles request orchestration, Pydantic validation, and response processing.

## Usage

Most LLM analyzers will need to be configured with the following parameters:

- `instruction`: the system instruction to guide the LLM's behavior.
- `api_key`: the API key to access the LLM provider's service.
- `pydantic_schema`: a [Pydantic model](https://docs.pydantic.dev/latest/concepts/models/) that defines the schema for the LLM's JSON response. 

The specific configuration options will depend on the analyzer's implementation. Here is an example using [`GeminiAnalyzer`][scraipe.extended.llm_analyzers.GeminiAnalyzer]. Note that you will need a [Gemini API key](https://ai.google.dev/gemini-api/docs/api-key).

1. Import dependencies and API key.

    ```python
    import os
    from scraipe.extended.llm_analyzers import GeminiAnalyzer
    from pydantic import BaseModel

    # Set using `export GEMINI_API_KEY=your-api-key`
    gemini_key = os.getenv("GEMINI_API_KEY")
    ```

2. Configure the analyzer with a prompt and schema.
    ```python
    # Craft an instruction for the LLM
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
    ```

3. Analyze and display results.
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

Running [our script](https://github.com/SnpM/scraipe/blob/main/examples/gemini_analyzer_example.py) outputs the extracted topic and sentiment of the article:

```bash
{'topic': 'web scraping and data analysis', 'sentiment': 'positive'}
```

## Conclusion

The topic & sentiment analyzer we configured can be plugged into a [basic workflow](../get_started/basic_workflow.md) for your project's needs. Consider pairing this analyzer with [NewsScraper][scraipe.extended.NewsScraper] to feed it the most relevant content from news sites.

Check out [celebrities_example.ipynb](https://github.com/SnpM/scraipe/blob/main/examples/celebrities_example.ipynb) for an advanced workflow using [`NewsScraper`][scraipe.extended.NewsScraper] and [`OpenAiAnalyzer`][scraipe.extended.OpenAiAnalyzer].

To integrate other LLMs, check out how to [write custom LLM scrapers](../advanced_usage/./extending_llm_analyzers.md).