import pytest
import pandas as pd
from scraipe.workflow import Workflow
from scraipe.classes import IScraper, IAnalyzer, ScrapeResult, AnalysisResult

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

class TestScrape:
    def test_scrape(self, workflow:Workflow):
        links = ["http://example.com/valid/1", "http://example.com/valid/2"]
        workflow.scrape(links)
        assert len(workflow.store) == 2
        for link in links:
            assert workflow.store[link].scrape_result.scrape_success

class TestAnalyze:
    def test_analyze(self, workflow):
        links = ["http://example.com/valid/1", "http://example.com/valid/2"]
        workflow.scrape(links)
        workflow.analyze()
        for link in links:
            assert workflow.store[link].analysis_result.analysis_success

class TestUpdateScrapes:
    def test_update_scrapes_list(self, workflow):
        result = ScrapeResult(link="http://example.com/updated", scrape_success=True, content="List content")
        workflow.update_scrapes([result])
        assert workflow.store["http://example.com/updated"].scrape_result.content == "List content"

    def test_update_scrapes_dict(self, workflow):
        result = ScrapeResult(link="http://example.com/dict", scrape_success=True, content="Dict content")
        workflow.update_scrapes({"http://example.com/dict": result})
        assert workflow.store["http://example.com/dict"].scrape_result.content == "Dict content"

    def test_update_scrapes_dataframe(self, workflow):
        data = {
            "link": ["http://example.com/df"],
            "scrape_success": [True],
            "content": ["DataFrame content"],
            "scrape_error": [None],
        }
        df = pd.DataFrame(data)
        workflow.update_scrapes(df)
        assert workflow.store["http://example.com/df"].scrape_result.content == "DataFrame content"

class TestUpdateAnalyses:
    def test_update_analyses_dict(self, workflow):
        result = AnalysisResult(analysis_success=True, output={"summry": "Dict analysis"})
        workflow.update_analyses({"http://example.com/dict_analysis": result})
        assert workflow.store["http://example.com/dict_analysis"].analysis_result.output["summary"] == "Dict analysis"

    def test_update_analyses_dataframe(self, workflow):
        data = {
            "link": ["http://example.com/df_analysis"],
            "analysis_success": [True],
            "analysis_error": [None],
            "summary": ["DataFrame analysis"],
        }
        df = pd.DataFrame(data)
        workflow.update_analyses(df, output_cols=["summary"])
        assert workflow.store["http://example.com/df_analysis"].analysis_result.output["summary"] == "DataFrame analysis"

class TestClearMethods:
    def test_clear_scrapes(self, workflow):
        links = ["http://example.com/valid/1"]
        workflow.scrape(links)
        workflow.clear_scrapes()
        for record in workflow.store.values():
            assert record.scrape_result is None

    def test_clear_analyses(self, workflow):
        links = ["http://example.com/valid/1"]
        workflow.scrape(links)
        workflow.analyze()
        workflow.clear_analyses()
        for record in workflow.store.values():
            assert record.analysis_result is None

    def test_clear_store(self, workflow):
        links = ["http://example.com/valid/1"]
        workflow.scrape(links)
        workflow.clear_store()
        assert workflow.store == {}

class TestScrapeOverwrite:
    def test_scrape_overwrite(self, workflow):
        links = ["http://example.com/valid/1"]
        # Initial scrape to populate the store
        workflow.scrape(links)
        # Artificially modify the content
        workflow.store["http://example.com/valid/1"].scrape_result.content = "Modified content"
        # Re-scrape with overwrite enabled
        workflow.scrape(links, overwrite=True)
        # Assert that the content is reset to the expected mocked content
        assert workflow.store["http://example.com/valid/1"].scrape_result.content == "Mocked content"

class TestStoreOperations:
    def test_get_scrapes(self, workflow):
        links = ["http://example.com/valid/1", "http://example.com/valid/2"]
        workflow.scrape(links)
        df = workflow.get_scrapes()
        assert not df.empty
        assert "link" in df.columns
        for link in links:
            assert link in df["link"].tolist()
            
    def test_get_analyses(self, workflow):
        links = ["http://example.com/valid/1", "http://example.com/valid/2"]
        workflow.scrape(links)
        workflow.analyze()
        df = workflow.get_analyses()
        assert not df.empty
        assert "link" in df.columns
        for link in links:
            assert not df[df["link"] == link].empty
            
    def test_dump_and_load_store(self, workflow):
        links = ["http://example.com/valid/1", "http://example.com/valid/2"]
        workflow.scrape(links)
        workflow.analyze()
        dump_df = workflow.dump_store()
        workflow.clear_store()
        assert workflow.store == {}
        workflow.load_store(dump_df, flush=True)
        for link in links:
            assert link in workflow.store
            record = workflow.store[link]
            assert record.scrape_result is not None or record.analysis_result is not None
            
    def test_export(self, workflow):
        links = ["http://example.com/valid/1", "http://example.com/valid/2"]
        workflow.scrape(links)
        workflow.analyze()
        export_df = workflow.export()
        assert len(export_df) == 2
        for col in ["link", "summary"]:
            assert col in export_df.columns
            
    def test_export_verbose(self, workflow):
        links = ["http://example.com/valid/1", "http://example.com/valid/2"]
        workflow.scrape(links)
        workflow.analyze()
        export_df = workflow.export(verbose=True)
        expected_cols = {"link", "scrape_success", "scrape_error", "analysis_success", "analysis_error"}
        assert expected_cols.issubset(set(export_df.columns))