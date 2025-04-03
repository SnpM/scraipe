import pytest
from scraipe.classes import AnalysisResult
from scraipe.async_classes import AsyncAnalyzerBase

# Dummy subclass with a concrete implementation for testing
class DummyAnalyzer(AsyncAnalyzerBase):
    async def async_analyze(self, content: str) -> AnalysisResult:
        # Dummy implementation returning a simple AnalysisResult
        output = {"analysis": f"analysis for {content}"}
        return AnalysisResult.success(output=output)

@pytest.mark.asyncio
async def test_async_analyze():
    analyzer = DummyAnalyzer()
    content = "sample content"
    result = await analyzer.async_analyze(content)
    assert result.output == {"analysis": f"analysis for {content}"}

def test_analyze():
    analyzer = DummyAnalyzer()
    content = "sample content"
    result = analyzer.analyze(content)
    assert result.output == {"analysis": f"analysis for {content}"}

def test_analyze_multiple():
    analyzer = DummyAnalyzer()
    contents = {"link1": "content1", "link2": "content2"}
    results = {}
    for link, result in analyzer.analyze_multiple(contents):
        results[link] = result
    assert len(results) == len(contents)
    for link, content in contents.items():
        assert results[link].output == {"analysis": f"analysis for {content}"}
