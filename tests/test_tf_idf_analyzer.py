import pytest
from scraipe.analyzers.text_statistics_analyzer import TfidfAnalyzer
from scraipe.classes import AnalysisResult

@pytest.fixture
def analyzer():
    return TfidfAnalyzer()

def test_analyze_single_document(analyzer):
    content = ["This is a test document."]
    result = analyzer.analyze(content)
    assert isinstance(result, AnalysisResult)
    assert result.success
    assert isinstance(result.content, dict)
    assert "test" in result.content

def test_analyze_multiple_documents(analyzer):
    content = [
        "This is the first document.",
        "This document is the second document.",
        "And this is the third one.",
    ]
    result = analyzer.analyze(content)
    assert isinstance(result, AnalysisResult)
    assert result.success
    assert isinstance(result.content, dict)
    assert "document" in result.content

def test_analyze_empty_content(analyzer):
    content = []
    result = analyzer.analyze(content)
    assert isinstance(result, AnalysisResult)
    assert result.success
    assert result.content == {}
