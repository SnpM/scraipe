import asyncio
import pytest
from scraipe.defaults.multi_analyzer import MultiAnalyzer
from scraipe.classes import AnalysisResult, IAnalyzer
from scraipe.async_classes import IAsyncAnalyzer

# Dummy synchronous analyzer that returns a unique key.
class DummySyncAnalyzer(IAnalyzer):
    def analyze(self, content: str) -> AnalysisResult:
        return AnalysisResult.succeed({"sync": f"processed {content}"})

# Dummy asynchronous analyzer that returns a unique key.
class DummyAsyncAnalyzer(IAsyncAnalyzer):
    async def async_analyze(self, content: str) -> AnalysisResult:
        await asyncio.sleep(0.01)
        return AnalysisResult.succeed({"async": f"processed {content}"})

def test_sync_analyze():
    content = "test_data"
    analyzer = DummySyncAnalyzer()
    multi = MultiAnalyzer(analyzers=[analyzer])
    result = multi.analyze(content)
    # Expect output with key 'sync'
    assert "sync" in result.output
    assert result.output["sync"] == f"processed {content}"

@pytest.mark.asyncio
async def test_async_analyze():
    content = "test_data"
    analyzer = DummyAsyncAnalyzer()
    multi = MultiAnalyzer(analyzers=[analyzer])
    result = await multi.async_analyze(content)
    # Expect output with key 'async'
    assert "async" in result.output
    assert result.output["async"] == f"processed {content}"

def test_conflict():
    content = "test_data"
    # Create two dummy analyzers that produce the same output key ("conflict") to trigger key conflict resolution.
    class DummySyncConflictAnalyzer(IAnalyzer):
        def analyze(self, content: str) -> AnalysisResult:
            return AnalysisResult.succeed({"conflict": f"sync {content}"})
    
    class DummyAsyncConflictAnalyzer(IAsyncAnalyzer):
        async def async_analyze(self, content: str) -> AnalysisResult:
            await asyncio.sleep(0.01)
            return AnalysisResult.succeed({"conflict": f"async {content}"})
    
    multi = MultiAnalyzer(analyzers=[DummySyncConflictAnalyzer(), DummyAsyncConflictAnalyzer()])
    result_sync = multi.analyze(content)
    
    # Expect first occurrence to remain under the original key and the second to be prefixed.
    expected_conflict_key = f"DummyAsyncConflictAnalyzer-1_conflict"
    for result in (result_sync,):
        assert isinstance(result, AnalysisResult)
        assert any("conflict" in key for key in result.output.keys())
        assert expected_conflict_key in result.output
        assert result.output[expected_conflict_key] == f"async {content}"

def test_no_analyzers():
    # Ensure that initializing with an empty list of analyzers fails.
    with pytest.raises(AssertionError):
        MultiAnalyzer(analyzers=[])
