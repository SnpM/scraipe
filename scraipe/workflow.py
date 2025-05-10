from typing import final, List, Dict, Generator
from scraipe.classes import IScraper, IAnalyzer, ScrapeResult, AnalysisResult
import pandas as pd
from pydantic import BaseModel, ValidationError
from tqdm.auto import tqdm
import logging
from logging import Logger
from functools import singledispatchmethod
import json

@final
class Workflow:
    """Orchestrates scraping and analysis processes.
    
    Attributes:
        scraper (IScraper): The scraper instance.
        analyzer (IAnalyzer): The analyzer instance.
        store (Dict[str, Workflow.StoreRecord]): Storage for scrape and analysis results keyed by link.
    """
    
    @final
    class StoreRecord:
        """Stores the scrape and analysis results for a specific link."""
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
    store:Dict[str, StoreRecord]
    def __init__(self, scraper:IScraper, analyzer:IAnalyzer,
        logger:Logger = None):
        self.scraper = scraper
        self.analyzer = analyzer
        self.store = {}
        self.logger = logger if logger else logging.getLogger(__name__)
    
    def scrape_generator(self, links:List[str]) -> Generator[ScrapeResult, None, None]:
        """Scrape content from the provided links.
        
        Removes duplicate links and filters out those already scraped (unless 'overwrite' is True).
        
        Args:
            links (List[str]): List of URLs to scrape.
            overwrite (bool): If True, re-scrape links already present in the store.
        """
        assert isinstance(self.scraper, IScraper), "Scraper must be an instance of IScraper"
        assert isinstance(links, list), "Links must be a list of strings"
        
 
        scrapes = {}
        # Update the scrape store
        try:
            for url, result in self.scraper.scrape_multiple(links):
                scrapes[url] = result
                if url not in self.store:
                    self.store[url] = self.StoreRecord(url)
                self.store[url].scrape_result = result

                # Sanity check: ensure content is not None when success is True
                if result.scrape_success and result.content is None:
                    self.logger.warning(f"Scrape result for {url} is successful but content is None.")
                    self.store[url].scrape_result = ScrapeResult.fail(url, "Content is None")
                yield result
        except Exception as e:
            self.logger.error(f"Error during scraping: {e}. Halting.")
            
        # Print summary
        success_count = sum(1 for result in scrapes.values() if result.scrape_success)
        self.logger.info(f"Successfully scraped {success_count}/{len(links)} links.")
    
    def scrape(self, links:List[str], overwrite:bool=False) -> List[ScrapeResult]:
        """Scrape content from the provided links and return a list of ScrapeResult objects.
        
        Args:
            links (List[str]): List of URLs to scrape.
            overwrite (bool): If True, re-scrape links already present in the store.
            
        Returns:
            List[ScrapeResult]: List of ScrapeResult objects for each link.
        """
        
        # Remove duplicates
        links_to_scrape = list(set(links))
        
        # Filter out the links that have already been succesfully scraped
        if not overwrite:
            links_to_scrape = [url for url in links if url not in self.store or self.store[url].scrape_result is None]
        
        generator = self.scrape_generator(links_to_scrape)
        results = []
        for result in tqdm(generator, desc="Scraping", unit="link", total=len(links_to_scrape)):
            results.append(result)
        return results
    
    def get_scrapes(self) -> pd.DataFrame:
        """Return a DataFrame copy of the stored scrape results."""
        records = self.store.values()
        scrape_results = [record.scrape_result for record in records if record.scrape_result is not None]     
        return pd.DataFrame([result.model_dump() for result in scrape_results])
        
    @singledispatchmethod
    def update_scrapes(self, data):
        """
        Update scrapes using different input data types.
        
        This generic dispatcher supports updating scrape results using:
          - A list of ScrapeResults
          - A dictionary mapping links (str) to ScrapeResults
          - A pandas DataFrame containing ScrapeResult fields in columns
        
        Raises:
            NotImplementedError: If the data type is not supported.
        """
        raise NotImplementedError(f"Cannot update scrapes with data of type {type(data)}")
    
    @update_scrapes.register(list)
    def _(self, data:List[ScrapeResult]):
        """
        Update the store's ScrapeResults with a list of ScrapeResult objects.
        
        Args:
            data (List[ScrapeResult]): List containing ScrapeResult instances.
        
        Side Effects:
            Updates the internal store with the provided scrape results.
        """
        # Assert input type
        assert isinstance(data, list)
        assert all(isinstance(result, ScrapeResult) for result in data)
        
        for result in data:
            if result.link not in self.store:
                self.store[result.link] = self.StoreRecord(result.link)
            self.store[result.link].scrape_result = result
            self.logger.info(f"Updated scrape result for {result.link}.")
            
    @update_scrapes.register(dict)
    def _(self, data:Dict[str,ScrapeResult]):
        """
        Update the store's ScrapeResults with a dictionary mapping links to ScrapeResult objects.
        
        Args:
            data (Dict[str, ScrapeResult]): Dictionary where keys are URLs and values are ScrapeResult instances.
        
        Side Effects:
            Validates that each key matches the ScrapeResult.link and updates the internal store.
        """
        # Assert input type
        assert isinstance(data, dict)
        assert all(isinstance(link, str) & isinstance(result, ScrapeResult) for link, result in data.items())
        
        results:List[ScrapeResult] = []
        for link, result in data.items():
            assert link == result.link, f"Link {link} does not match ScrapeResult link {result.link}"
            results.append(result)
        self.update_scrapes(results)
            
    @update_scrapes.register(pd.DataFrame)
    def _(self, data:pd.DataFrame):
        """
        Update the store's ScrapeResults from a pandas DataFrame.
        
        The DataFrame contains the following columns to construct a list of ScrapeResults:
        - 'link': The URL of the scraped content.
        - 'scrape_success': A boolean indicating if the scrape was successful.
        - 'scrape_error': The error message if the scrape failed; mandatory if 'scrape_success' is False.
        - 'content': The content scraped from the URL.
        
        Args:
            data (pd.DataFrame): DataFrame containing scrape result information.
        
        Side Effects:
            Attempts to create ScrapeResult from each DataFrame row and updates the internal store.
        """
        # Assert input type
        assert isinstance(data, pd.DataFrame)
        assert all(col in data.columns for col in ["link", "scrape_success", "scrape_error", "content"])
        
        # Create a ScrapeResult from each row
        # If it fails, log the error and continue
        results:List[ScrapeResult] = []
        for i, row in data.iterrows():
            try:
                result = ScrapeResult(**row.to_dict())
            except ValidationError as e:
                self.logger.info(f"Failed to update scrape result {row}. Error: {e}")
            else:
                results.append(result)
        self.update_scrapes(results)
        
    @singledispatchmethod
    def update_analyses(self, data, output_cols:List[str]=None):
        """
        Update analyses using different input data types.
        
        This generic dispatcher supports updating analysis results using:
          - A dictionary mapping links (str) to AnalysisResult objects
          - A pandas DataFrame containing a 'links' column and AnalysisResult information
        
        Raises:
            NotImplementedError: If the data type is not supported.
        """
        raise NotImplementedError(f"Cannot update analyses with data of type {type(data)}")
    
    @update_analyses.register(dict)
    def _(self, data:Dict[str,AnalysisResult]):
        """
        Update the store's AnalysisResults with a dictionary mapping links to AnalysisResult objects.
        Args:
            data (Dict[str, AnalysisResult]): Dictionary where keys are links and values are AnalysisResult instances.
        Side Effects:
            Validates that each key matches the AnalysisResult.link and updates the internal store.
        """
        # Assert types of input
        assert isinstance(data, dict)
        assert all(isinstance(link, str) & isinstance(result, AnalysisResult) for link, result in data.items())
        
        for link, result in data.items():
            if link not in self.store:
                self.store[link] = self.StoreRecord(link)
            self.store[link].analysis_result = result
            self.logger.info(f"Updated analysis result for {link}.")
            
    @update_analyses.register(pd.DataFrame)
    def _(self, data:pd.DataFrame, output_cols:List[str]):
        """
        Update the store's AnalysisResults from a pandas DataFrame.
        
        The DataFrame should contain the following columns;
        - 'link': The URL of the scraped content.
        - 'analysis_success': A boolean indicating if the analysis was successful.
        - 'analysis_error': The error message if the analysis failed; mandatory if 'analysis_success' is False.
        - Columns corresponding to output_cols: The output extracted from analysis.

        
        Args:
            data (pd.DataFrame): DataFrame containing analysis result information.
        
        Side Effects:
            Attempts to create AnalysisResult from each DataFrame row and updates the internal store.
        """
        # Assert input type
        assert isinstance(data, pd.DataFrame)
        assert all(col in data.columns for col in ["link", "analysis_success", "analysis_error"] + output_cols)
        
        # Try to create an AnalysisResult from each row
        link_result_map:Dict[str, AnalysisResult] = {}
        for i, row in data.iterrows():
            link = row["link"]
            # Extract outputs dictionary from output_cols
            output = {col: row[col] for col in output_cols}
            # Just set output to None if all values are None
            if all(value is None for value in output.values()):
                output = None
            try:
                # Create AnalysisResult
                result = AnalysisResult(
                    analysis_success=row["analysis_success"],
                    analysis_error=row["analysis_error"],
                    output=output
                )
            except ValidationError as e:
                self.logger.info(f"Failed to update analysis result {row}. Error: {e}")
            else:
                link_result_map[link] = result
                
        # Update the store with the link-result mapping
        self.update_analyses(link_result_map)
        
    def clear_scrapes(self):
        """Clear all ScrapeResults from the store."""
        for record in self.store.values():
            record.scrape_result = None
        self.logger.info("Cleared all scrape results.")
        
    def clear_analyses(self):
        """Clear all AnalysisResults from the store."""
        for record in self.store.values():
            record.analysis_result = None
        self.logger.info("Cleared all analysis results.")
        
    def clear_store(self):
        """Erase all records of scraped and analyzed content."""
        self.store = {}
        self.logger.info("Flushed all records from the store.")
    
    def analyze_generator(self, links:List[str]) -> Generator[AnalysisResult, None, None]:
        """Analyze content for links that have been successfully scraped but not yet analyzed.
        
        Args:
            overwrite (bool): (Currently unused) Reserved for future re-analysis capabilities.
        """
        assert isinstance(self.analyzer, IAnalyzer), "Analyzer must be an instance of IAnalyzer"
        assert isinstance(self.store, dict), "Store must be a dictionary"

        content_dict = {}
        for link in links:
            if link not in self.store:
                self.logger.warning(f"Link {link} not found in store. Skipping.")
                continue
            if self.store[link].scrape_result is None:
                self.logger.warning(f"Scrape result for {link} is None. Skipping.")
                continue
            if self.store[link].scrape_result.scrape_success is False:
                self.logger.warning(f"Scrape result for {link} is not successful. Skipping.")
                continue
            if self.store[link].scrape_result.content is None:
                self.logger.warning(f"Scrape result for {link} has no content. Skipping.")
                continue
            content_dict[link] = self.store[link].scrape_result.content
        
        # update the store
        analyses = {}
        try:
            for link, result in self.analyzer.analyze_multiple(content_dict):
                self.store[link].analysis_result = result
                analyses[link] = result
                yield result
        except Exception as e:
            self.logger.error(f"Error during analysis: {e}. Halting.")
                
        # Print summary
        success_count = sum([1 for result in analyses.values() if result.analysis_success])
        self.logger.info(f"Successfully analyzed {success_count}/{len(content_dict)} links.")
        
    def analyze(self, overwrite:bool=False) -> List[AnalysisResult]:
        """Analyze content for links that have been successfully scraped but not yet analyzed.
        
        Args:
            overwrite (bool): (Currently unused) Reserved for future re-analysis capabilities.
            
        Returns:
            List[AnalysisResult]: List of AnalysisResult objects for each link.
        """
                
        # Get list of links to analyze
        links_with_content = []
        links_to_analyze = []
        for record in self.store.values():
            if record.scrape_result is not None and record.scrape_result.scrape_success:
                links_with_content.append(record.link)
                if overwrite or record.analysis_result is None:
                    links_to_analyze.append(record.link)
                    
        self.logger.info(f"Analyzing {len(links_to_analyze)}/{len(links_with_content)} new or retry links with content...")
        
        generator = self.analyze_generator(links_to_analyze)
        results = []
        for result in tqdm(generator, desc="Analyzing", unit="link", total=len(links_to_analyze)):
            results.append(result)
        return results
    
    def get_analyses(self) -> pd.DataFrame:
        """Return a DataFrame copy of the stored analysis results."""
        records = self.store.values()
        rows = []
        for record in records:
            # Create a row with link column followed by the analysis result columns
            row = {"link": record.link}
            if record.analysis_result is not None:
                row.update(record.analysis_result.model_dump())
                rows.append(row)
        return pd.DataFrame(rows)
    
    def update_records(self, records:List[StoreRecord]):
        """Update records in the store.
        
        Args:
            records (List[StoreRecord]): List of StoreRecord objects to replace the current store.
        """
        # Assert input type
        assert isinstance(records, list)
        assert all(isinstance(record, self.StoreRecord) for record in records)
        assert all(record.link is not None for record in records)
        
        self.store.update({record.link: record for record in records})
        self.logger.info(f"Updated {len(records)} records.")
        
    def dump_store(self) -> pd.DataFrame:
        """Dump the store to a DataFrame that can be loaded later."""
        records = self.store.values()
        
        # Dump ScrapeResult and AnalysisResult fields to a DataFrame
        rows = []
        for record in records:
            row = {"link": record.link}
            if record.scrape_result is not None:
                row.update(record.scrape_result.model_dump())
            if record.analysis_result is not None:
                row.update(record.analysis_result.model_dump())
            rows.append(row)
        
        # Get columns from Pydantic models fields
        columns = [col for col in ScrapeResult.model_fields.keys()] + \
            [col for col in AnalysisResult.model_fields.keys()]
        
        df = pd.DataFrame(rows, columns=columns)
        
        # Transform the "output" column to JSON string for serialization
        df['output'] = df['output'].apply(lambda x: json.dumps(x))
        
        return df
    
    def load_store(self, df:pd.DataFrame, flush:bool=True):
        """Load the store from a DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame containing scrape and analysis results.
            flush (bool): If True, clear the current store before loading.
        """
        # Assert input type
        assert isinstance(df, pd.DataFrame)
        
        if flush:
            self.clear_store()
            
        # Create StoreRecord objects from the DataFrame
        records = []
        for _, row in df.iterrows():
            record = self.StoreRecord(link=row["link"])
            row_dict = row.to_dict()
            try:
                record.scrape_result = ScrapeResult(**row_dict)
            except ValidationError as e:
                pass
            
            try:
                record.analysis_result = AnalysisResult(**row_dict)
            except ValidationError as e:
                pass
            records.append(record)
            
        # Transform the "output" column from JSON string to dictionary
        for record in records:
            if record.analysis_result is not None and isinstance(record.analysis_result.output, str):
                try:
                    record.analysis_result.output = json.loads(record.analysis_result.output)
                except json.JSONDecodeError as e:
                    self.logger.info(f"Failed to decode JSON for {record.link}. Error: {e}")
        self.update_records(records)
        
    def export(self, verbose=False) -> pd.DataFrame:
        """Export stored records as a DataFrame with unnested analysis outputs.
        
        If verbose is True, include extra metadata such as success flags and error messages.
        
        Args:
            verbose (bool): If True, include additional columns for detailed status.
            
        Returns:
            pd.DataFrame: A DataFrame containing exported records.
        """
        records = self.store.values()
        pretty_df = pd.DataFrame()
        
        # Add link column
        pretty_df["link"] = [record.link for record in records]
        
        if verbose:
            # Add success and error columns
            pretty_df["scrape_success"] = [record.scrape_result.scrape_success if record.scrape_result else False for record in records]
            pretty_df["scrape_error"] = [record.scrape_result.scrape_error if record.scrape_result else None for record in records]
            pretty_df["analysis_success"] = [record.analysis_result.analysis_success if record.analysis_result else False for record in records]
            pretty_df["analysis_error"] = [record.analysis_result.analysis_error if record.analysis_result else None for record in records]
        
        outputs = [record.analysis_result.output if record.analysis_result else None for record in records]
        # output column contains dictionary or None. Unnest it
        unnested = pd.json_normalize(outputs)
        # Add the unnested columns to the pretty_df
        pretty_df = pd.concat([pretty_df, unnested], axis=1)
        return pretty_df
