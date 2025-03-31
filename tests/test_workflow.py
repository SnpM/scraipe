import pytest
from scraipe.workflow import Workflow
from scraipe.classes import IScraper, IAnalyzer, ScrapeResult, AnalysisResult
import pandas as pd

class MockScraper(IScraper):
    def scrape(self, url):
        if "valid" in url:
            return ScrapeResult(link=url, scrape_success=True, content="Mocked content")
        return ScrapeResult(link=url, scrape_success=False, scrape_error="Invalid link")

class MockAnalyzer(IAnalyzer):
    def analyze(self, content):
        return AnalysisResult(analysis_success=True, output={"summary": "Mocked summary"})

@pytest.fixture
def workflow():
    scraper = MockScraper()
    analyzer = MockAnalyzer()
    return Workflow(scraper, analyzer)

def test_scrape(workflow):
    links = ["http://example.com/valid/1", "http://example.com/valid/2"]
    workflow.scrape(links)
    assert len(workflow.store) == 2
    for link in links:
        assert workflow.store[link].scrape_result.scrape_success

def test_analyze(workflow):
    links = ["http://example.com/valid/1", "http://example.com/valid/2"]
    workflow.scrape(links)
    workflow.analyze()
    for link in links:
        assert workflow.store[link].analysis_result.analysis_success

def test_get_records(workflow):
    links = ["http://example.com/valid/1", "http://example.com/valid/2"]
    workflow.scrape(links)
    workflow.analyze()
    records_df = workflow.get_records()
    assert len(records_df) == 2
    assert "link" in records_df.columns
    assert "scrape_success" in records_df.columns
    assert "analysis_success" in records_df.columns

def test_update_records(workflow):
    data = {
        "link": ["http://example.com/1"],
        "scrape_success": [True],
        "content": ["Updated content"],
        "analysis_success": [True],
        "output": [{"summary": "Updated summary"}],
    }
    df = pd.DataFrame(data)
    workflow.update_records(df)
    assert len(workflow.store) == 1
    assert workflow.store["http://example.com/1"].scrape_result.content == "Updated content"
    assert workflow.store["http://example.com/1"].analysis_result.output["summary"] == "Updated summary"

def test_export(workflow):
    links = ["http://example.com/valid/1", "http://example.com/valid/2"]
    workflow.scrape(links)
    workflow.analyze()
    export_df = workflow.export()
    assert len(export_df) == 2
    assert "link" in export_df.columns
    assert "scrape_success" in export_df.columns
    assert "analysis_success" in export_df.columns
    assert "summary" in export_df.columns
