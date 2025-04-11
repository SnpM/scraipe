import os
import pytest
import asyncio
import pydantic
from unittest.mock import patch, AsyncMock

from scraipe.extended.llm_analyzers.gemini_analyzer import GeminiAnalyzer

# Dummy response to simulate genai.GenerativeModel.generate_content return value
class DummyResponse:
    def __init__(self, text):
        self.text = text

class MockSchema(pydantic.BaseModel):
    location: str

TEST_INSTRUCTION = 'Extract the city from the content. Return a JSON object with the following schema: {"location": "city"}'
TEST_CONTENT = "Last summer, I visited Paris!"

@pytest.fixture
def analyzer():
    return GeminiAnalyzer(
        api_key="test_api_key",
        instruction=TEST_INSTRUCTION,
        pydantic_schema=MockSchema,
        model="gemini-2.0-flash"
    )

@pytest.fixture
def live_analyzer():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set; skipping live test.")
    return GeminiAnalyzer(
        api_key=api_key,
        instruction=TEST_INSTRUCTION,
        pydantic_schema=MockSchema,
        model="gemini-2.0-flash"
    )

@pytest.mark.asyncio
async def test_query_live(live_analyzer):
    if live_analyzer is None:
        pytest.skip("No GEMINI_API_KEY found; set GEMINI_API_KEY to run live test.")
    result = await live_analyzer.query_llm(TEST_CONTENT, TEST_INSTRUCTION)
    assert isinstance(result, str)
    assert len(result) > 0

@pytest.mark.asyncio
async def test_analyze_live(live_analyzer):
    result = await live_analyzer.async_analyze(TEST_CONTENT)
    output = result.output
    print(f"Live test output: {output}")
    assert output is not None
    assert "location" in output

@pytest.mark.asyncio
async def test_query_llm(analyzer):
    dummy_text = '{"location": "Paris"}'
    with patch.object(analyzer.client.aio.models, 'generate_content', return_value=DummyResponse(dummy_text)):
        result = await analyzer.query_llm(TEST_CONTENT, TEST_INSTRUCTION)
        assert result == dummy_text

@pytest.mark.asyncio
async def test_analyze_valid_response(analyzer):
    valid_json = '{"location": "Paris"}'
    with patch.object(analyzer, 'query_llm', new_callable=AsyncMock) as mock_query:
        mock_query.return_value = valid_json
        result = await analyzer.async_analyze(TEST_CONTENT)
        output = result.output
        assert output == {"location": "Paris"}

@pytest.mark.asyncio
async def test_analyze_invalid_json(analyzer):
    invalid_json = "Invalid JSON"
    with patch.object(analyzer, 'query_llm', new_callable=AsyncMock) as mock_query:
        mock_query.return_value = invalid_json
        result = await analyzer.async_analyze(TEST_CONTENT)
        assert not result.analysis_success
        assert "not a valid json string" in result.analysis_error

@pytest.mark.asyncio
async def test_analyze_schema_validation_failure(analyzer):
    invalid_schema_json = '{"wrong_key": "value"}'
    with patch.object(analyzer, 'query_llm', new_callable=AsyncMock) as mock_query:
        mock_query.return_value = invalid_schema_json
        result = await analyzer.async_analyze(TEST_CONTENT)
        assert not result.analysis_success
        assert "schema" in result.analysis_error

@pytest.mark.asyncio
async def test_validate_method(analyzer):
    with patch("scraipe.extended.llm_analyzers.gemini_analyzer.Client") as MockClient:
        mock_client_instance = MockClient.return_value
        mock_client_instance.models.get.return_value = "mock_model_instance"
        
        analyzer.validate(api_key="test_api_key", model="gemini-2.0-flash", test_client=mock_client_instance)
        mock_client_instance.models.get.assert_called_once_with(model="gemini-2.0-flash")