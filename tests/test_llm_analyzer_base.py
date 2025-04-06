import pytest
from pydantic import BaseModel, ValidationError
from scraipe.extended.llm_analyzers.llm_analyzer_base import LlmAnalyzerBase
from scraipe.classes import AnalysisResult

class MockAnalyzer(LlmAnalyzerBase):
    """Mock implementation of LlmAnalyzerBase for testing."""
    async def query_llm(self, content: str, instruction: str) -> str:
        if "error" in content:
            raise Exception("Mock LLM error")
        if "invalid_json" in content:
            return "invalid json"
        if "schema_fail" in content:
            return '{"key": "value"}'
        return '{"valid_key": "valid_value"}'

class MockSchema(BaseModel):
    valid_key: str

@pytest.mark.asyncio
async def test_async_analyze_success():
    analyzer = MockAnalyzer(instruction="Test instruction", pydantic_schema=MockSchema)
    result = await analyzer.async_analyze("valid content")
    assert result.success
    assert result.output == {"valid_key": "valid_value"}

@pytest.mark.asyncio
async def test_async_analyze_invalid_content():
    analyzer = MockAnalyzer(instruction="Test instruction")
    result = await analyzer.async_analyze("")
    assert not result.success
    assert result.error == "Content is not a valid string."

@pytest.mark.asyncio
async def test_async_analyze_content_size_limit():
    analyzer = MockAnalyzer(instruction="Test instruction", max_content_size=5)
    result = await analyzer.async_analyze("content exceeding limit")
    assert result.success
    assert result.output == {"valid_key": "valid_value"}

@pytest.mark.asyncio
async def test_async_analyze_query_llm_error():
    analyzer = MockAnalyzer(instruction="Test instruction")
    result = await analyzer.async_analyze("error")
    assert not result.success
    assert "Failed to query LLM" in result.error

@pytest.mark.asyncio
async def test_async_analyze_invalid_json():
    analyzer = MockAnalyzer(instruction="Test instruction")
    result = await analyzer.async_analyze("invalid_json")
    assert not result.success
    assert "LLM response is not a valid json string" in result.error

@pytest.mark.asyncio
async def test_async_analyze_schema_validation_fail():
    analyzer = MockAnalyzer(instruction="Test instruction", pydantic_schema=MockSchema)
    result = await analyzer.async_analyze("schema_fail")
    assert not result.success
    assert "OpenAI response does not follow the pydantic schema" in result.error