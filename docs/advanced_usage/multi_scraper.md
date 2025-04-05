# MultiScraper Tutorial

This tutorial explains how to use and extend the MultiScraper for scraping multiple types of URLs.

## Overview

MultiScraper is designed to handle links by delegating the scrape request to appropriate scrapers based on predefined ingress rules. If none of the rules match, a fallback scraper is used. This design allows flexible and fault-tolerant scraping.

## How It Works

- **Ingress Rules**: Each rule consists of a regex pattern and an associated scraper. If a URL matches the pattern, the corresponding scraper is used.
- **Fallback Scraper**: A scraper that is used when none of the ingress rules succeed.
- **Error Preservation**: When enabled, errors from failed scraping attempts are preserved for debugging.

## Usage

1. **Define Ingress Rules**  
    Create rules by specifying a regex pattern and a scraper that implements `IScraper`. These rules will be evaluated in order until one returns a successful `ScrapeResult`.
    Below is an example of how to define ingress rules.

    ```python
    from scraipe.extended.multi_scraper import IngressRule
    from scraipe.extended import NewsScraper, AiohttpScraper
    ingress_rules = [
        # Use NewsScraper for links containing "news", "article", or "story"
        IngressRule(
            r"(news|article|story)",
            scraper=NewsScraper()
        ),
        # Fallback to AiohttpScraper
        IngressRule(
            r".*",
            scraper=AiohttpScraper()
        ),
    ]
    ```

2. **Creating MultiScraper**  
   Pass a list of ingress rules and a fallback scraper when creating an instance of `MultiScraper`:
   ```python
   multi_scraper = MultiScraper(ingress_rules=ingress_rules, fallback_scraper=aiohttp_scraper)
   ```

3. **Scraping a URL**  
   Use the `async_scrape` method to scrape a URL:
   ```python
   result = await multi_scraper.async_scrape("https://example.com")
   if result.scrape_success:
       print("Scrape successful:", result.data)
   else:
       print("Scrape failed:", result.scrape_error)
   ```

## Example: Defining Ingress Rules


## Extending MultiScraper

1. **Custom Ingress Rules**  
   You can extend the functionality by creating new ingress rules that match specific URL patterns and assign custom scrapers.

2. **Custom Scraper Implementations**  
   Create a new scraper by extending `IScraper` or `IAsyncScraper` to implement your custom scraping logic.

3. **Integration with Other Components**  
   Combine MultiScraper with custom analyzers to process the scraped data further. See the [Custom Components](./custom_components.md) tutorial for more details.

## Tips

- Test each custom scraper in isolation before integrating it with MultiScraper.
- Enable error preservation during development to capture and debug failures.
- Extend ingress rules easily by matching new URL patterns with your custom scrapers.

Happy scraping!