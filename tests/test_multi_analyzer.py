import pytest
import asyncio
from scraipe.classes import AnalysisResult, IAnalyzer
from scraipe.async_classes import IAsyncAnalyzer
from scraipe.defaults.multi_analyzer import MultiAnalyzer

# Dummy sync analyzer that always succeeds
class DummySyncAnalyzerSuccess(IAnalyzer):
    def analyze(self, content):
        return AnalysisResult.succeed({"sync_key": "sync_value"})

# Dummy sync analyzer that always fails
class DummySyncAnalyzerFailure(IAnalyzer):
    def analyze(self, content):
        return AnalysisResult.fail("sync failure")

# Dummy async analyzer that always succeeds
class DummyAsyncAnalyzerSuccess(IAsyncAnalyzer):
    async def async_analyze(self, content):
        await asyncio.sleep(0)
        return AnalysisResult.succeed({"async_key": "async_value"})

# Dummy async analyzer that always fails
class DummyAsyncAnalyzerFailure(IAsyncAnalyzer):
    async def async_analyze(self, content):
        await asyncio.sleep(0)
        return AnalysisResult.fail("async failure")

# Dummy analyzers for conflict resolution: both return same key "common"
class DummySyncAnalyzerConflict(IAnalyzer):
    def analyze(self, content):
        return AnalysisResult.succeed({"common": "sync_conflict"})

class DummyAsyncAnalyzerConflict(IAsyncAnalyzer):
    async def async_analyze(self, content):
        await asyncio.sleep(0)
        return AnalysisResult.succeed({"common": "async_conflict"})

def test_single_sync_success():
    analyzer = DummySyncAnalyzerSuccess()
    ma = MultiAnalyzer([analyzer], debug=True)
    result = ma.analyze("content")
    assert result.analysis_success is True
    assert result.output.get("sync_key") == "sync_value"
    assert "SUCCESS" in result.error

def test_single_sync_failure():
    analyzer = DummySyncAnalyzerFailure()
    ma = MultiAnalyzer([analyzer], debug=True)
    result = ma.analyze("content")
    assert result.analysis_success is False
    assert "sync failure" in result.error

def test_single_async_success():
    analyzer = DummyAsyncAnalyzerSuccess()
    ma = MultiAnalyzer([analyzer], debug=True)
    result = ma.analyze("content")
    assert result.analysis_success is True
    assert result.output.get("async_key") == "async_value"
    assert "SUCCESS" in result.error

def test_multiple_analyzers_conflict():
    sync_analyzer = DummySyncAnalyzerConflict()
    async_analyzer = DummyAsyncAnalyzerConflict()
    ma = MultiAnalyzer([sync_analyzer, async_analyzer], debug=True)
    result = ma.analyze("content")
    # Both analyzers succeed so conflict resolution should occur.
    # Expect output keys to be renamed due to conflict.
    assert result.analysis_success is True
    conflicts = [key for key in result.output.keys() if "common" in key]
    assert len(conflicts) == 2
    assert result.error.count("SUCCESS") == 2

def test_all_fail():
    sync_analyzer = DummySyncAnalyzerFailure()
    async_analyzer = DummyAsyncAnalyzerFailure()
    ma = MultiAnalyzer([sync_analyzer, async_analyzer], debug=True)
    result = ma.analyze("content")
    assert result.analysis_success is False
    assert "sync failure" in result.error
    assert "async failure" in result.error

def test_mixed_sync_async():
    sync_analyzer = DummySyncAnalyzerSuccess()
    async_analyzer = DummyAsyncAnalyzerSuccess()
    ma = MultiAnalyzer([sync_analyzer, async_analyzer], debug=True)
    result = ma.analyze("content")
    assert result.analysis_success is True
    # Check that both analyzers provided their unique keys
    assert result.output.get("sync_key") == "sync_value"
    assert result.output.get("async_key") == "async_value"
    # Both analyzers succeeded so their debug indications should be present
    assert result.error.count("SUCCESS") == 2