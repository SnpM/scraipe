"""Contains analyzers for various cloud-based LLM provider integrations."""

from scraipe.extended.llm_analyzers.llm_analyzer_base import LlmAnalyzerBase

# Import OpenAiAnalyzer
try:
    import openai
except ImportError: 
    print("OpenAI API is not available. Please install the openai package.")
else:
    from scraipe.extended.llm_analyzers.openai_analyzer import OpenAiAnalyzer

# Import GeminiAnalyzer
try:
    import google.genai
except ImportError:
    print("Gemini API is not available. Please install the google.genai package.")
else:
    from scraipe.extended.llm_analyzers.gemini_analyzer import GeminiAnalyzer