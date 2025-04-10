# Custom Components

Scrapers and analyzers are modular, so you can extend the functionality on existing components or make new ones to suit your data needs.

## Custom Scrapers

To create a custom scraper, extend [`IScraper`][scraipe.classes.IScraper] and implement `scrape()`. The `scrape()` method should return an instance of [`ScrapeResult`][scraipe.classes.ScrapeResult] that can be created via `ScrapeResult.fail() `or `ScrapeResult.succeed()`.

[`ExampleScraper`](https://github.com/SnpM/scraipe/blob/main/examples/example_custom_components.py) is a minimal implementation that simply captures the URL.

```python
from scraipe.classes import IScraper, ScrapeResult
class ExampleScraper(IScraper):
    """A minimal scraper implementation for example."""
    def scrape(self, url:str)->ScrapeResult:
        # Fail if url is malicious!
        if "hacker" in url:
            return ScrapeResult.fail(url, "Hacker detected!")
        # Simulate a successful scrape; simply returns the url
        content = f"I'm simply returning the {url}"
        return ScrapeResult.succeed(url, content)
```


To facilitate fault tolerance, `scrape()` implementations should not raise exceptions. Instead, debug and error information should be stored in `ScrapeResult.scrape_error`, a field that is set when you call `ScrapeResult.fail()`.

## Custom Analyzers

To create a custom analyzer, extend [`IAnalyzer`][scraipe.classes.IAnalyzer] and implement the `analyze()` method. [ExampleAnalyzer](https://github.com/SnpM/scraipe/blob/main/examples/example_custom_components.py) is a minimal implementation that reverses the content.

```python
from scraipe.classes import IAnalyzer, AnalysisResult
class ExampleAnalyzer(IAnalyzer):
    """A minimal analyzer implementation for example."""
    def analyze(self, content: str) -> AnalysisResult:
        # Fail if content is malicious!
        if "hacker" in content:
            return AnalysisResult.fail("Hacker detected!")
        # Simulate a successful analysis; reverses the content
        result = content[::-1]
        output = {"reversed_content": result}
        return AnalysisResult.succeed(output)
```

The `analyze()` method should return an instance of [`AnalysisResult`][scraipe.classes.AnalysisResult] that can be created via `AnalysisResult.fail() `or `AnalysisResult.succeed()`.

Similar to `IScraper.scrape()`, `analyze()` should not raise exceptions. Instead, any errors or debug information should stored in the an `AnalysisResult.analysis_result` attribute, which is set when you call `AnalysisResult.fail()` function.

## Async Scrapers and Analyzers

Scraping and analyzing often require IO-bound operations such as waiting for responses from the web. These operations should be optimized to run in parallel using asynchronous logic. Implementing asynchronous logic for components is just as simple. Instead of extending `IScraper` or `IAnalyzer`, extend the `IAsyncScraper` and `IAsyncAnalyzer` interfaces.

For async scrapers, implement `async_scrape()` using asynchronous code:

```python
import asyncio
from scraipe.async_classes import IAsyncScraper, IAsyncAnalyzer
class AsyncExampleScraper(IAsyncScraper):
    """An asynchronous example scraper implementation for example."""
    async def async_scrape(self, url: str) -> ScrapeResult:
        # Simulate waiting for a response
        await asyncio.sleep(1)
        
        # Fail if url is malicious!
        if "hacker" in url:
            return ScrapeResult.fail(url, "Hacker detected!")
        # Simulate a successful scrape; simply returns the url asynchronously
        content = f"I'm asynchronously returning the {url}"
        return ScrapeResult.succeed(url, content)
```

For async analyzers, implement `async_analyze()` using asynchronous code:

```python
import asyncio
from scraipe.async_classes import ScrapeResult, AnalysisResult
class AsyncExampleAnalyzer(IAsyncAnalyzer):
    """An asynchronous example analyzer implementation for example."""
    async def async_analyze(self, content: str) -> AnalysisResult:
        # Simulate waiting for analysis
        await asyncio.sleep(1)
        
        # Fail if content is malicious!
        if "hacker" in content:
            return AnalysisResult.fail("Hacker detected!")
        # Simulate a successful analysis; reverses the content
        result = content[::-1]
        output = {"reversed_content": result}
        return AnalysisResult.succeed(output)
```


[TextScraper][scraipe.defaults.TextScraper] and [LlmAnalyzerBase][scraipe.extended.llm_analyzers.LlmAnalyzerBase] are more complete examples of asynchronous component implementations.

To learn more about Scraipe's asynchronous orchestration, check out [Async Architecture](./async_architecture.md).