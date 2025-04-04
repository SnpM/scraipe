from typing import final, List, Dict
from scraipe.classes import IScraper, IAnalyzer, ScrapeResult, AnalysisResult
import pandas as pd
from pydantic import BaseModel, ValidationError
from tqdm import tqdm
import logging
from logging import Logger

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
    def __init__(self, scraper:IScraper, analyzer:IAnalyzer,
        logger:Logger = None):
        self.scraper = scraper
        self.analyzer = analyzer
        self.thread_count = 1
        self.store = {}
        self.logger = logger if logger else logging.getLogger(__name__)
        
    def scrape(self, links:List[str], overwrite:bool=False):
        """Scrape the content from the given links."""
        # Remove duplicates
        links = list(set(links))
        
        # Filter out the links that have already been scraped
        if overwrite:
            links_to_scrape = links
        else:
            links_to_scrape = []
            for url in links:
                if url not in self.store or self.store[url].scrape_result is None or self.store[url].scrape_result.scrape_success == False:
                    # If the link is not in the store or the scrape result is None or failed, add it to the list
                    links_to_scrape.append(url)
        self.logger.info(f"Scraping {len(links_to_scrape)}/{len(links)} new or retry links...")
        
        scrapes = {}
        # Update the scrape store
        with tqdm(total=len(links_to_scrape), desc="Scraping", unit="link") as pbar:
            try:
                for url, result in self.scraper.scrape_multiple(links_to_scrape):
                    scrapes[url] = result
                    if url not in self.store:
                        self.store[url] = self.StoreRecord(url)
                    self.store[url].scrape_result = result

                    # Sanity check: ensure content is not None when success is True
                    if result.scrape_success and result.content is None:
                        self.logger.info(f"Warning: Scrape result for {url} is successful but content is None.")
                        self.store[url].scrape_result = ScrapeResult(link=url, scrape_success=False, scrape_error="Content is None.")
                    pbar.update(1)
            except Exception as e:
                self.logger.error(f"Error during scraping: {e}. Halting.")
            
        # Print summary
        success_count = sum(1 for result in scrapes.values() if result.scrape_success)
        self.logger.info(f"Successfully scraped {success_count}/{len(links_to_scrape)} links.")
    
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
                self.logger.error(f"Failed to update scrape result {row}. Error: {e}")
                continue
            if result.link not in self.store:
                self.store[result.link] = self.StoreRecord(result.link, result)
            self.store[result.link].scrape_result = result
        self.logger.info(f"Updated {len(state_store_df)} scrape results.")
    
    def analyze(self, overwrite:bool=False):
        """Analyze the unanalyzed content in the scrape store."""
        # Get list of links to analyze
        links_with_content = []
        for record in self.store.values():
            if record.scrape_result is not None and record.scrape_result.scrape_success:
                links_with_content.append(record.link)
        
                    
        links_to_analyze = [link for link in links_with_content if self.store[link].analysis_result is None]
            
        self.logger.info(f"Analyzing {len(links_to_analyze)}/{len(links_with_content)} new or retry links with content...")
        
        # Analyze the content
        content_dict = {link: self.store[link].scrape_result.content for link in links_to_analyze}
        assert all([content is not None for content in content_dict.values()])
        # update the store
        analyses = {}
        num_items = len(content_dict)
        # Use tqdm to show progress
        with tqdm(total=num_items, desc="Analyzing", unit="item") as pbar:
            try:
                for link, result in self.analyzer.analyze_multiple(content_dict):
                    self.store[link].analysis_result = result
                    analyses[link] = result
                    # update the progress bar
                    pbar.update(1)
            except Exception as e:
                self.logger.error(f"Error during analysis: {e}. Halting.")
                    
        # Print summary
        success_count = sum([1 for result in analyses.values() if result.analysis_success])
        self.logger.info(f"Successfully analyzed {success_count}/{len(content_dict)} links.")
    
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
                self.logger.info(f"Failed to update analysis result {row}. Error: {e}")
                continue
            if result.link not in self.store:
                self.store[result.link] = self.StoreRecord(result.link)
            self.store[result.link].analysis_result = result
        self.logger.info(f"Updated {len(state_store_df)} analysis results.")
    
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
        self.logger.info(f"Updated {len(state_store_df)} records.")
    
    def export(self) -> pd.DataFrame:
        """Export links and unnested outputs."""
        records = self.store.values()
        pretty_df = pd.DataFrame()
        
        # Add link column
        pretty_df["link"] = [record.link for record in records]
        
        # Add success columns for scrape and analysis
        pretty_df["scrape_success"] = [record.scrape_result.scrape_success if record.scrape_result else False for record in records]
        pretty_df["analysis_success"] = [record.analysis_result.analysis_success if record.analysis_result else False for record in records]
        
        outputs = [record.analysis_result.output if record.analysis_result else None for record in records]
        # output column contains dictionary or None. Unnest it
        unnested = pd.json_normalize(outputs)
        # Add the unnested columns to the pretty_df
        pretty_df = pd.concat([pretty_df, unnested], axis=1)
        return pretty_df
