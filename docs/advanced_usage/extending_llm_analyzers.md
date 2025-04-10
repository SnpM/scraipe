# Custom LLM Scrapers

Scraipe supports LLM-powered feature extraction for advanced content parsing with [LLM scrapers](../get_started/using_llm_analyzers.md). This page explains how to integrate a custom LLM into Scraipe by creating your own LLM scraper.

## Overview
[LlmAnalyzerBase][scraipe.extended.llm_analyzers.LlmAnalyzerBase] is an abstract base class that provides a common interface for LLM analyzers. The class:

- Orchestrates asynchronous requests to the LLM.
- Abstracts API-specific details by delegating the `query_llm()` implementation to subclasses.
- Ensures consistent LLM JSON responses with a user-defined Pydantic schema.

## Steps to Create a Custom Analyzer
1. **Extend LlmAnalyzerBase**  
   Create your analyzer class that inherits from `LlmAnalyzerBase`.

2. **Set up the analyzer in `__init__()`**  
   This could involve authenticating with a cloud-based LLM provider or initializing a model from a local LLM package.
   
      Always call `super().__init__()` in your child's `__init__()` function to initialize shared properties such as `instruction`, `pydantic_schema`, `max_content_size`, and `max_workers`. This ensures that your analyzer is configured to perform the common `LlmAnalyzerBase` logic.

3. **Implement query_llm()**  
   Define the asynchronous method `query_llm(content: str, instruction: str)` that:

      - Prepares the request for your LLM.
      - Sends the request using your chosen client library.
      - Returns the JSON response as a string.

## Examples

### GeminiAnalyzer Example
The [`GeminiAnalyzer`](https://github.com/SnpM/scraipe/blob/main/scraipe/extended/llm_analyzers/gemini_analyzer.py) and [`OpenAiAnalyzer`](https://github.com/SnpM/scraipe/blob/main/scraipe/extended/llm_analyzers/openai_analyzer.py) implementations showcase:

- Initializing a client from a cloud-based LLM provider.
- Configuring a request from the provided instruction, content, and Pydantic schema.
- Returning the LLM provider's response.