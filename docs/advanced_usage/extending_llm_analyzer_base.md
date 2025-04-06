# Custom LLM Scrapers

Scraipe supports Large Language Model (LLM)-powered feature extraction for advanced content parsing with [LLM scrapers](../get_started/using_llm_analyzers.md). This page explains how to integrate a custom LLM by creating your own LLM scraper.

## Overview
[LlmAnalyzerBase][scraipe.extended.llm_analyzers.LlmAnalyzerBase] is an abstract base class that provides a common interface for LLM analyzers. The class:

- Manages content size limitations and orchestrates asynchronous requests to the LLM.
- Abstracts API-specific details by delegating the `query_llm()` implementation to subclasses.
- Validates the LLM's JSON response using a user-defined Pydantic schema, ensuring consistent output.

## Steps to Create a Custom Analyzer
1. **Extend LlmAnalyzerBase**  
   Create your analyzer class that inherits from `LlmAnalyzerBase`.

2. **Call `super().__init__` in the Child Class**  
   - Always call `super().__init__()` to initialize shared properties such as `instruction`, `pydantic_schema`, `max_content_size`, and `max_workers`.
   - This ensures that your analyzer is correctly configured with Scraipe's common logic before adding implementation-specific behavior.

3. **Implement query_llm()**  
   Define the asynchronous method `query_llm(content: str, instruction: str) -> str` that:
   - Prepares the request for your LLM.
   - Sends the request using your chosen client library.
   - Returns the JSON response as a string.

4. **Configure and Validate**  
   Utilize a Pydantic schema to validate the JSON response, ensuring consistency and correctness.

## Examples

### GeminiAnalyzer Example
The [`GeminiAnalyzer`](https://github.com/SnpM/scraipe/blob/main/scraipe/extended/llm_analyzers/gemini_analyzer.py) showcases:
- Initializing a Gemini API client with an API key.
- Building a configuration from the provided instruction, content, and Pydantic schema.
- Generating a response with Gemini.

### OpenAiAnalyzer Example
The [`OpenAiAnalyzer`](https://github.com/SnpM/scraipe/blob/main/scraipe/extended/llm_analyzers/openai_analyzer.py) showcases:
- Setting up an asynchronous OpenAI client.
- Sending chat messages containing system instructions and content.
- Generating a response with OpenAI.

This guide follows the pattern used in our guide, so you can configure and utilize your custom analyzer in a similar way within your projects.