from abc import ABC, abstractmethod
from typing import final, List, Dict, Generator, Tuple
import tqdm
from pydantic import BaseModel, model_validator
from re import Pattern

@final
class ScrapeResult(BaseModel):
    
    # Note: It's recommended to use success() and fail() methods to create instances of ScrapeResult.
    link: str
    content:str|None = None
    scrape_success:bool
    scrape_error:str|None = None
    metadata:dict|None = None
    
    @property
    def success(self) -> bool:
        """Indicates whether the scraping operation was successful.
        
        Returns:
            bool: True if scraping succeeded; otherwise False.
        """
        return self.scrape_success
    
    @property
    def error(self) -> str:
        """Provides the error message if the scraping operation failed. May also contain debug information for successful scrapes.
        
        Returns:
            str: The error message when scraping fails, or None if successful.
        """
        return self.scrape_error
    
    def __str__(self):
        return f"ScrapeResult(link={self.link}, content={self.content}, success={self.scrape_success}, error={self.scrape_error}, metadata={self.metadata})"
    
    def __repr__(self):
        return str(self)
    
    @model_validator(mode='after')
    def _validate(self):
        # Ensure content is present if scrape_success is True
        if self.scrape_success and self.content is None:
            raise ValueError("Content must be provided if scrape_success is True.")
        # Ensure error is present if scrape_success is False
        if not self.scrape_success and self.scrape_error is None:
            raise ValueError("Error must be provided if scrape_success is False.")
        return self
    
    @staticmethod
    def succeed(link: str, content: str, metadata:dict = None) -> 'ScrapeResult':
        """Creates a ScrapeResult instance for a successful scraping operation.
        
        Args:
            link (str): The URL that was scraped.
            content (str): The content fetched from the link.
            metadata (dict): Additional data scraped from the link.
        
        Returns:
            ScrapeResult: An instance with scrape_success set to True.
        """
        assert link is not None, "Link must be provided"
        assert content is not None, "Content must be provided for success"

        
        return ScrapeResult(
            link=link,
            content=content,
            scrape_success=True,
            metadata = metadata
        )
    
    @staticmethod
    def fail(link: str, error: str) -> 'ScrapeResult':
        """Creates a ScrapeResult instance for a failed scraping operation.
        
        Args:
            link (str): The URL attempted.
            error (str): The error message describing the failure.
        
        Returns:
            ScrapeResult: An instance with scrape_success set to False.
        """
        assert isinstance(link,str), "Link must be provided"
        assert isinstance(error,str), "Error must be populated for failure"
        return ScrapeResult(
            link=link,
            scrape_success=False,
            scrape_error=error,
        )

@final
class AnalysisResult(BaseModel):
    output:dict|None = None
    analysis_success:bool
    analysis_error:str|None = None
    
    @property
    def success(self) -> bool:
        """Indicates whether the analysis operation was successful.
        
        Returns:
            bool: True if analysis succeeded; otherwise False.
        """
        return self.analysis_success
    
    @property
    def error(self) -> str:
        """Provides the error message if the analysis operation failed.
        
        Returns:
            str: Provides the error message when analysis fails. May also contain debug information for successful analyses.
        """
        return self.analysis_error
    
    def __str__(self):
        return f"AnalysisResult(output={self.output}, success={self.analysis_success}, error={self.analysis_error})"
    
    def __repr__(self):
        return str(self)
    
    @model_validator(mode='after')
    def _validate(self):
        # Ensure output is present if analysis_success is True
        if self.analysis_success and self.output is None:
            raise ValueError("Output must be provided if analysis_success is True.")
        # Ensure error is present if analysis_success is False
        if not self.analysis_success and self.analysis_error is None:
            raise ValueError("Error must be provided if analysis_success is False.")
        return self
    
    @staticmethod
    def succeed(output: dict) -> 'AnalysisResult':
        """Creates an AnalysisResult instance for a successful analysis operation.
        
        Args:
            output (dict): The extracted analysis data.
        
        Returns:
            AnalysisResult: An instance with analysis_success set to True.
        """
        return AnalysisResult(
            analysis_success=True,
            output=output
        )
    
    @staticmethod
    def fail(error: str) -> 'AnalysisResult':
        """Creates an AnalysisResult instance for a failed analysis operation.
        
        Args:
            error (str): The error message detailing the failure.
        
        Returns:
            AnalysisResult: An instance with analysis_success set to False.
        """
        return AnalysisResult(
            analysis_success=False,
            analysis_error=error
        )

class IScraper(ABC):
    @abstractmethod
    def scrape(self, link: str) -> ScrapeResult:
        """Fetches content from the specified URL.
        
        Args:
            link (str): The URL to scrape.
        
        Returns:
            ScrapeResult: The result of the scraping operation.
        """
        raise NotImplementedError()

    def scrape_multiple(self, links: List[str]) -> Generator[Tuple[str, ScrapeResult], None, None]:
        """Get content from multiple urls."""
        for link in links:
            result = self.scrape(link)
            yield link, result
    
    def get_expected_link_format(self) -> str|Pattern:
        """Returns the expected regex format for links compatible with the scraper. Returning None indicates compatibility with any link format.
        
        Returns:
            str: The expected link format as a regex string or compiled pattern.
        """
        return None

class IAnalyzer(ABC):
    @abstractmethod
    def analyze(self, content: str) -> AnalysisResult:
        """Analyzes the provided content to extract structured information.
        
        Args:
            content (str): The text content to analyze.
        
        Returns:
            AnalysisResult: The result containing analysis output or error details.
        """
        raise NotImplementedError()
    
    def analyze_multiple(self, contents: Dict[str, str]) -> Generator[Tuple[str, AnalysisResult], None, None]:
        """Analyze multiple contents."""
        for link, content in contents.items():
            result = self.analyze(content)
            yield link, result
