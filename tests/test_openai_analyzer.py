import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock

from scraipe.extended.llm_analyzers import OpenAiAnalyzer
import pydantic

TARGET_MODULE = OpenAiAnalyzer.__module__

class MockSchema(pydantic.BaseModel):
    location: str

TEST_INSTRUCTION = '''Extract the city from the content. Return a JSON object with the following schema: {"location": "[city]"}'''
TEST_CONTENT = "This Summer, I vacationed in Rome!"

@pytest.fixture
def analyzer():
    return OpenAiAnalyzer(
        api_key="test_api_key",
        organization="",
        instruction=TEST_INSTRUCTION,
        pydantic_schema=MockSchema,
        model="gpt-4o-mini"
    )
    
@pytest.fixture
def live_analyzer():
    # Load the OpenAI API key from the environment
    import os
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAiAnalyzer(
        api_key=api_key,
        organization="",
        instruction=TEST_INSTRUCTION,
        pydantic_schema=MockSchema,
        model="gpt-4o-mini"
    )
    
@pytest.mark.asyncio
async def test_query_live(live_analyzer):
    if live_analyzer is None:
        pytest.skip("No OpenAI API key found in the environment. Set the OPENAI_API_KEY environment variable to run this test.")
    result = await live_analyzer.query_llm(TEST_CONTENT, TEST_INSTRUCTION)
    assert isinstance(result, str)
    assert len(result) > 0

@pytest.mark.asyncio
async def test_analyze_live(live_analyzer):
    if live_analyzer is None:
        pytest.skip("No OpenAI API key found in the environment. Set the OPENAI_API_KEY environment variable to run this test.")
    result = await live_analyzer.async_analyze(TEST_CONTENT)
    output = result.output
    assert output is not None
    assert "location" in output
    assert output["location"] == "Rome"

@patch(f"{TARGET_MODULE}.OpenAiAnalyzer.query_llm", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_analyze_valid_response(mock_query_llm, analyzer):
    mock_query_llm.return_value = '{"location": "value"}'
    content = TEST_CONTENT
    result = await analyzer.async_analyze(content)
    output = result.output
    assert output == {"location": "value"}

@patch(f"{TARGET_MODULE}.OpenAiAnalyzer.query_llm", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_analyze_invalid_json(mock_query_llm, analyzer):
    mock_query_llm.return_value = "Invalid JSON"
    content = TEST_CONTENT
    analysis_result = await analyzer.async_analyze(content)
    assert not analysis_result.analysis_success
    assert "not a valid json string" in analysis_result.analysis_error

@patch(f"{TARGET_MODULE}.OpenAiAnalyzer.query_llm", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_analyze_schema_validation_failure(mock_query_llm, analyzer):
    mock_query_llm.return_value = '{"invalid_key": "value"}'
    content = TEST_CONTENT
    analysis_result = await analyzer.async_analyze(content)
    assert not analysis_result.analysis_success
    assert "schema" in analysis_result.analysis_error