from typing import final, List, Dict
from scraipe.classes import IScraper, IAnalyzer, ScrapeResult, AnalysisResult
import pandas as pd
from pydantic import BaseModel, ValidationError

@final
class Workflow:
    @final
    class StoreRecord:
        """Stores the scrape and analysis results for a link."""
        link:str
        scrape_result:ScrapeResult
        analysis_result:AnalysisResult
        def __init__(self, link:str):
            self.link = link
            self.scrape_result = None
            self.analysis_result = None
        
        def __str__(self):
            return f"StoreRecord(link={self.link}, scrape_result={self.scrape_result}, analysis_result={self.analysis_result})"
        def __repr__(self):
            return str(self)
    
    scraper:IScraper
    analyzer:IAnalyzer
    thread_count:int 
    store:Dict[str, StoreRecord]
    def __init__(self, scraper:IScraper, analyzer:IAnalyzer):
        self.scraper = scraper
        self.analyzer = analyzer
        self.thread_count = 1
        self.store = {}
        
    def scrape(self, links:List[str], overwrite:bool=False):
        """Scrape the content from the given links."""
        # Remove duplicates
        links = list(set(links))
        
        # Filter out the links that have already been scraped
        if overwrite:
            links_to_scrape = links
        else:
            links_to_scrape = []
            for link in links:
                if link not in self.store or self.store[link].scrape_result is None:
                    links_to_scrape.append(link)
        print (f"Scraping {len(links_to_scrape)}/{len(links)} new or failed links...")
        
        scrapes:Dict[ScrapeResult] = self.scraper.scrape_multiple(links_to_scrape)
        
        # Update the scrape store
        for link, result in scrapes.items():
            if link not in self.store:
                self.store[link] = self.StoreRecord(link)
            self.store[link].scrape_result = result
        
        # Print summary
        success_count = sum([1 for result in scrapes.values() if result.success])
        print(f"Successfully scraped {success_count}/{len(links_to_scrape)} links.")
    
    def get_scrapes(self) -> pd.DataFrame:
        """Return a copy of the store's scrape results as a DataFrame"""
        records = self.store.values()
        scrape_results = [record.scrape_result for record in records if record.scrape_result is not None]     
        return pd.DataFrame([result.model_dump() for result in scrape_results])
        
        
        
    def flush_store(self):
        """Erase all the previously scraped anad analyzed content"""
        self.store = {}
        
    def update_scrapes(self, state_store_df:pd.DataFrame):
        """Update the store from a dataframe"""
        for i, row in state_store_df.iterrows():
            try:
                result = ScrapeResult(**row)
            except ValidationError as e:
                print(f"Failed to update scrape result {row}. Error: {e}")
                continue
            if result.link not in self.store:
                self.store[result.link] = self.StoreRecord(result.link, result)
            self.store[result.link].scrape_result = result
        print(f"Updated {len(state_store_df)} scrape results.")
    
    def analyze(self, overwrite:bool=False):
        """Analyze the unanalyzed content in the scrape store."""
        # Get list of links to analyze
        if overwrite:
            links_to_analyze = [record.link for record in self.store.values() if record.scrape_result is not None]
        else:
            links_to_analyze = [record.link for record in self.store.values() if record.scrape_result is not None and record.analysis_result is None]
        print(f"Analyzing {len(links_to_analyze)}/{len(self.store)} new or failed links...")
        
        # Analyze the content
        content_dict = {record.link:record.scrape_result.content for record in self.store.values() if record.scrape_result is not None}
        assert len(content_dict) == len(links_to_analyze)
        assert all([content is not None for content in content_dict.values()])
        
        analyses:Dict[AnalysisResult] = self.analyzer.analyze_multiple(content_dict)
        
        # Update the store
        for link, result in analyses.items():
            self.store[link].analysis_result = result
        
        # Print summary
        success_count = sum([1 for result in analyses.values() if result.success])
        print(f"Successfully analyzed {success_count}/{len(links_to_analyze)} links.")
    
    def get_analyses(self) -> pd.DataFrame:
        """Return a copy of the store's analysis results as a DataFrame"""
        records = self.store.values()
        rows = []
        for record in records:
            # Create a row with link column followed by the analysis result columns
            row = {"link": record.link}
            if record.analysis_result is not None:
                row.update(record.analysis_result.model_dump())
            rows.append(row)
        return pd.DataFrame(rows)
    
    def update_analyses(self, state_store_df:pd.DataFrame):
        """Update the store from a dataframe"""
        for i, row in state_store_df.iterrows():
            try:
                result = AnalysisResult(**row)
            except ValidationError as e:
                print(f"Failed to update analysis result {row}. Error: {e}")
                continue
            if result.link not in self.store:
                self.store[result.link] = self.StoreRecord(result.link)
            self.store[result.link].analysis_result = result
        print(f"Updated {len(state_store_df)} analysis results.")
    
    def get_records(self) -> pd.DataFrame:
        """Return a copy of the store's records as a DataFrame"""
        rows = []
        for record in self.store.values():
            row = {"link": record.link}
            if record.scrape_result is not None:
                row.update(record.scrape_result.model_dump())
            if record.analysis_result is not None:
                row.update(record.analysis_result.model_dump())
            rows.append(row)
        return pd.DataFrame(rows)
    
    def update_records(self, state_store_df:pd.DataFrame):
        """Update the store from a dataframe"""
        for i, row in state_store_df.iterrows():
            # Create a record from the row
            record = self.StoreRecord(row["link"])
            if "content" in row:
                record.scrape_result = ScrapeResult(**row)
            if "output" in row:
                record.analysis_result = AnalysisResult(**row)
            self.store[row["link"]] = record
        print(f"Updated {len(state_store_df)} records.")
    
    def export(self) -> pd.DataFrame:
        """Export links and unnested outputs."""
        raw_df = self.get_analyses()
        pretty_df = pd.DataFrame()
        
        # Add link column
        pretty_df["link"] = raw_df["link"]
        
        # output column contains dictionary or None. Unnest it
        unnested = pd.json_normalize(raw_df["output"])
        pretty_df = pd.concat([pretty_df, unnested], axis=1)
        return pretty_df
