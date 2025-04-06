from scraipe.extended.llm_analyzers.llm_analyzer_base import LlmAnalyzerBase

# Try openai
try:
    import openai
except ImportError: 
    print("OpenAI API is not available. Please install the openai package.")
else:
    from scraipe.extended.llm_analyzers.openai_analyzer import OpenAiAnalyzer

# Try gemini
