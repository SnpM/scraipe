from abc import ABC, abstractmethod
from typing import final, List, Dict, Generator, Tuple
import tqdm
from pydantic import BaseModel

@final
class ScrapeResult(BaseModel):
    
    # Note: It's recommended to use success() and fail() methods to create instances of ScrapeResult.
    link:str
    content:str = None
    scrape_success:bool
    scrape_error:str = None
    
    def __str__(self):
        return f"ScrapeResult(link={self.link}, content={self.content}, success={self.scrape_success}, error={self.scrape_error})"
    def __repr__(self):
        return str(self)
    
    @staticmethod
    def success(link: str, content: str) -> 'ScrapeResult':
        """Creates a ScrapeResult for a successful scrape."""
        return ScrapeResult(
            link=link,
            content=content,
            scrape_success=True
        )
    
    @staticmethod
    def fail(link: str, error: str) -> 'ScrapeResult':
        """Creates a ScrapeResult for a failed scrape."""
        return ScrapeResult(
            link=link,
            scrape_success=False,
            scrape_error=error
        )

@final
class AnalysisResult(BaseModel):
    output:dict = None
    analysis_success:bool
    analysis_error:str = None
    
    def __str__(self):
        return f"AnalysisResult(output={self.output}, success={self.analysis_success}, error={self.analysis_error})"
    def __repr__(self):
        return str(self)
    
    @staticmethod
    def success(output:dict) -> 'AnalysisResult':
        """Creates an AnalysisResult for a successful run."""
        return AnalysisResult(
            analysis_success=True,
            output=output
        )
    
    @staticmethod
    def fail(error:str) -> 'AnalysisResult':
        """Creates an AnalysisResult for an unsuccessful run."""
        return AnalysisResult(
            analysis_success=False,
            analysis_error=error
        )

class IScraper(ABC):
    @abstractmethod
    def scrape(self, url:str)->ScrapeResult:
        """Get content from the url"""
        raise NotImplementedError()

    def scrape_multiple(self, urls: List[str]) -> Generator[Tuple[str, ScrapeResult], None, None]:
        """Get content from multiple urls."""
        for url in urls:
            result = self.scrape(url)
            yield url, result

class IAnalyzer(ABC):
    @abstractmethod
    def analyze(self, content: str) -> AnalysisResult:
        """Analyze the content and return the extracted information as a dict."""
        raise NotImplementedError()
    
    def analyze_multiple(self, contents: Dict[str, str]) -> Generator[Tuple[str, AnalysisResult], None, None]:
        """Analyze multiple contents."""
        for link, content in contents.items():
            result = self.analyze(content)
            yield link, result
