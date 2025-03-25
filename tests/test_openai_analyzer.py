import pytest
from unittest.mock import patch, MagicMock
from scraipe.analyzers.openai_analyzer import OpenAiAnalyzer
import pydantic

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
    api_key = None
    if "OPENAI_API_KEY" in os.environ:
        api_key = os.environ["OPENAI_API_KEY"]
    else:
        return None
    
    return OpenAiAnalyzer(
        api_key=api_key,
        organization="",
        instruction=TEST_INSTRUCTION,
        pydantic_schema=MockSchema,
        model="gpt-4o-mini"
    )
    
def test_query_live(live_analyzer):
    if live_analyzer is None:
        pytest.skip("No OpenAI API key found in the environment. Set the OPENAI_API_KEY environment variable to run this test.")
        return
    result = live_analyzer.query_openai(TEST_CONTENT)
    assert isinstance(result, str)
    assert len(result) > 0

def test_analyze_live(live_analyzer):
    if live_analyzer is None:
        pytest.skip("No OpenAI API key found in the environment. Set the OPENAI_API_KEY environment variable to run this test.")
        return
    result = live_analyzer.analyze(TEST_CONTENT)
    output = result.output
    assert output is not None
    assert "location" in output
    assert output["location"] == "Rome"


@patch("scraipe.analyzers.openai_analyzer.OpenAiAnalyzer.query_openai")
def test_analyze_valid_response(mock_query_openai, analyzer):
    mock_query_openai.return_value = '{"location": "value"}'

    content = TEST_CONTENT
    result = analyzer.analyze(content)
    output = result.output
    assert output == {"location": "value"}


@patch("scraipe.analyzers.openai_analyzer.OpenAiAnalyzer.query_openai")
def test_analyze_invalid_json(mock_query_openai, analyzer):
    mock_query_openai.return_value = "Invalid JSON"

    content = TEST_CONTENT
    analysis_result = analyzer.analyze(content)
    assert not analysis_result.success
    assert "not a valid json string" in analysis_result.error


@patch("scraipe.analyzers.openai_analyzer.OpenAiAnalyzer.query_openai")
def test_analyze_schema_validation_failure(mock_query_openai, analyzer):
    mock_query_openai.return_value = '{"invalid_key": "value"}'

    content = TEST_CONTENT
    analysis_result = analyzer.analyze(content)
    assert not analysis_result.success
    assert "schema" in analysis_result.error