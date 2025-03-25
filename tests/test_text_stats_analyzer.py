import pytest
from scraipe.analyzers.text_stats_analyzer import TextStatsAnalyzer
from scraipe.classes import AnalysisResult

@pytest.fixture
def analyzer():
    return TextStatsAnalyzer()

def test_analyze_basic_text(analyzer):
    content = "Hello world! This is a test."
    result = analyzer.analyze(content)
    assert isinstance(result, AnalysisResult)
    assert result.success
    assert result.output["word_count"] == 6
    assert result.output["character_count"] == 28
    assert result.output["sentence_count"] == 2
    assert result.output["average_word_length"] == pytest.approx(3.5, rel=1e-2)

def test_analyze_empty_text(analyzer):
    content = ""
    result = analyzer.analyze(content)
    assert isinstance(result, AnalysisResult)
    assert result.success
    assert result.output["word_count"] == 0
    assert result.output["character_count"] == 0
    assert result.output["sentence_count"] == 0
    assert result.output["average_word_length"] == 0

def test_analyze_text_with_special_characters(analyzer):
    content = "Hello, world!!! How's it going? Great, I hope."
    result = analyzer.analyze(content)
    assert isinstance(result, AnalysisResult)
    assert result.success
    assert result.output["word_count"] == 8
    assert result.output["character_count"] == 46
    assert result.output["sentence_count"] == 3
    assert result.output["average_word_length"] == pytest.approx(4, rel=1e-2)

def test_analyze_text_with_only_punctuation(analyzer):
    content = "!!! ??? ..."
    result = analyzer.analyze(content)
    assert isinstance(result, AnalysisResult)
    assert result.success
    assert result.output["word_count"] == 0
    assert result.output["character_count"] == 11
    assert result.output["sentence_count"] == 0
    assert result.output["average_word_length"] == 0
