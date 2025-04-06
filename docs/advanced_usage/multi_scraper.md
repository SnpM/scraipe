# MultiScraper Tutorial

This tutorial explains how to use and extend the [`MultiScraper`][scraipe.defaults.multi_scraper] to process diverse links.

## Overview

`MultiScraper` handles links by delegating scrape requests to appropriate scrapers based on predefined ingress rules. It's designed for flexible and fault-tolerant scraping.

## How It Works

- **Ingress Rules**: Each [`IngressRule`][scraipe.defaults.multi_scraper.IngressRule] consists of a regex pattern and an associated scraper. If a link matches the pattern, the corresponding scraper is used.
- **Rule Processing**: The rules are processed in order. If a rule succeeds, its result is immediately returned. If the rule passes or fails, subsequent rules have the opportunity to match and scrape the links.
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
2. **Creating the MultiScraper**  

    Pass a list of ingress rules and a fallback scraper when creating an instance of `MultiScraper`:

    ```python
    # Pass ingress rules into a new MultiScraper
    multi_scraper = MultiScraper(ingress_rules=ingress_rules)
    ```
    []()
3. **Scraping a URL**  
    Use the `async_scrape` method to scrape a URL:
    
    ```python
    result = await multi_scraper.async_scrape("https://example.com")
    if result.scrape_success:
        print("Scrape successful:", result.data)
    else:
        print("Scrape failed:", result.scrape_error)
    ```

## Extending MultiScraper

1. **Custom Ingress Rules**  
   Craft an ingress rules to assign links to specific scrapers for your project's needs.

2. **Custom Scraper Implementations**  
   Extend `IScraper` or `IAsyncScraper` to implement your [custom scraping logic](./custom_components.md).

## Tips

- Test each custom scraper in isolation before integrating it with MultiScraper.
- Enable error preservation during development to capture and debug failure chains.
- Leverage [built-in scrapers] provided by Scraipe.