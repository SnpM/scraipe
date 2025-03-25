from abc import ABC, abstractmethod
from typing import final, List, Dict
import tqdm
from pydantic import BaseModel

@final
class ScrapeResult(BaseModel):
    link:str
    content:str = None
    success:bool
    error:str = None
    
    def __str__(self):
        return f"ScrapeResult(link={self.link}, content={self.content}, success={self.success}, error={self.error})"
    def __repr__(self):
        return str(self)

@final
class AnalysisResult(BaseModel):
    output:dict = None
    success:bool
    error:str = None
    
    def __str__(self):
        return f"AnalysisResult(output={self.output}, success={self.success}, error={self.error})"
    def __repr__(self):
        return str(self)

class IScraper(ABC):
    @abstractmethod
    def scrape(self, url:str)->ScrapeResult:
        """Get content from the url"""
        raise NotImplementedError()

    def scrape_multiple(self, urls: List[str]) -> Dict[str, ScrapeResult]:
        """Get content from multiple urls."""
        results = {}
        for url in tqdm.tqdm(urls, desc="Scraping URLs"):
            result = self.scrape(url)
            results[url] = result
        return results

class IAnalyzer(ABC):
    @abstractmethod
    def analyze(self, content: str) -> AnalysisResult:
        """Analyze the content and return the extracted information as a dict."""
        raise NotImplementedError()
    
    def analyze_multiple(self, contents: Dict[str, str]) -> Dict[str, AnalysisResult]:
        """Analyze multiple contents."""
        results = {}
        for link, content in tqdm.tqdm(contents.items(), desc="Analyzing content"):
            result = self.analyze(content)
            results[link] = result
        return results