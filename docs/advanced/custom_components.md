# Custom Components

Scrapers and analyzers are modular, so you can extend the functionality on existing components or make new ones to suit your data needs.

## Custom Scrapers

To create a custom scraper, extend `IScraper` and implement `scrape()`. [ExampleScraper](https://github.com/SnpM/scraipe/blob/main/scraipe/defaults/examples.py) is a minimal implementation that simply captures the URL.

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
        return ScrapeResult.success(url, content)
```

The `scrape()` method should return an instance of `ScrapeResult` that can be created via `ScrapeResult.fail() `or `ScrapeResult.success()`.

To facilitate fault tolerance, `scrape()` implementations should not raise exceptions. Instead, debug and error information can be stored in `ScrapeResult.scrape_error`, a field that is set when you call `ScrapeResult.fail()`.

## Custom Analyzers

To create a custom analyzer, extend `IAnalyzer` and implement the `analyze()` method. [ExampleAnalyzer](https://github.com/SnpM/scraipe/blob/main/scraipe/defaults/examples.py) demonstrates a minimal implementation that reverses the content.

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
        return AnalysisResult.success(output)
```

The `analyze()` method should return an instance of `AnalysisResult` that can be created via `AnalysisResult.fail() `or `AnalysisResult.success()`.

Similar to `IScraper.scrape()` implementations, `analyze()` should not raise exceptions. Instead, any errors or debug information should be captured in the `AnalysisResult` object, which can be set using `AnalysisResult.fail()`.

## Async Scrapers and Analyzers

`IAsyncScraper` and `IAsyncAnalyzer` provide the respective `async_scrape()` and `async_analyze()` methods. Instead of implementing custom logic in synchronous functions, you can write lightning fast asynchronous code using these async interfaces.

The synchronous integration is seamless. A call to `IAsyncScraper.scrape_multiple()` from a synchronous context will automatically use `AsyncManager` to run `IAsyncScraper.async_scrape()` for all links asynchronously and progressively yield the results as they complete.

[AiohttpScraper](https://github.com/SnpM/scraipe/blob/main/scraipe/extended/aiohttp_scraper.py) and [LlmAnalyzerBase](https://github.com/SnpM/scraipe/blob/main/scraipe/extended/llm_analyzers.py) are examples of how to extend the async interfaces.