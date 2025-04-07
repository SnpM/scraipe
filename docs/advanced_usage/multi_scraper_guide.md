# MultiScraper Guide

[`MultiScraper`][scraipe.defaults.multi_scraper] handles links by delegating scrape requests to appropriate scrapers based on customizable ingress rules. It's designed for flexible and fault-tolerant scraping of links that could be different types of documents.

This page explains how to tailor `MultiScraper` for specific news and non-news links.

## How It Works

- **Ingress Rules**: Each [`IngressRule`][scraipe.defaults.multi_scraper.IngressRule] consists of a regex pattern and an associated scraper. If a link matches the pattern, the corresponding scraper is used.
- **Rule Processing**: The rules are processed in order. If a rule succeeds, its result is immediately returned. If the rule skips or fails execution, subsequent rules have the opportunity to match and scrape the links.
- **Error Preservation**: When enabled, errors from failed scraping attempts are preserved for debugging.

## Usage

1. **Define Ingress Rules**  
    Create rules by specifying a regex pattern and an instance of a class that implements [`IScraper`][scraipe.classes.IScraper]. These rules will be evaluated in order until one returns a successful `ScrapeResult`.

    ```python
    from scraipe.defaults import IngressRule, MultiScraper, TextScraper
    from scraipe.extended import NewsScraper

    # Define ingress rule for news links and TextScraper fallback
    ingress_rules = [
        # Use NewsScraper for links containing "news", "article", or "story"
        IngressRule(
            r"(news|article|story)",
            scraper=NewsScraper()
        ),
        # Fallback to TextScraper
        IngressRule(
            r".*",
            scraper=TextScraper()
        ),
    ]
    ```
2. **Creating the MultiScraper**  

    Pass a list of ingress rules and a fallback scraper when creating an instance of `MultiScraper`. Note that setting `debug=True` will save information about processed ingress rules in the result's error field. 

    ```python
    # Instantiate a new MultiScraper with our custom ingress rules
    multi_scraper = MultiScraper(ingress_rules=ingress_rules, debug=True)
    ```
    []()
3. **Scrape**  
    Use the `scrape` method to test your `MultiScraper` on a news link an a non-news link.
    
    ```python
    # Scrape a news link
    link = "https://apnews.com/article/studio-ghibli-chatgpt-images-hayao-miyazaki-openai-0f4cb487ec3042dd5b43ad47879b91f4"
    result = multi_scraper.scrape(link)

    print ("=== News Link ===")
    print("Content:", result.content[0:400])
    print("Debug Info:", result.error) # Ingress debug chain stored in error

    # Scrape a non-news link
    link = "https://www.example.com/"
    result = multi_scraper.scrape(link)

    print ("\n=== Non-News Link ===")
    print("Content:",result.content[0:400])
    print("Debug Info:", result.error) # Ingress debug chain stored in error
    ```

Running [this script](https://github.com/SnpM/scraipe/blob/main/examples/multiscraper_example.py) will output the content and debug info from processing the different links. Notice how the news link used NewsScraper while the non-news link used TextScraper, as expected based on our ingress rules.

```bash
=== News Link ===
Content: ChatGPT’s viral Studio Ghibli-style images highlight AI copyright concerns
LOS ANGELES (AP) — Fans of Studio Ghibli, the famed Japanese animation studio behind “Spirited Away” and other beloved movies, were delighted this week when a new version of ChatGPT let them transform popular internet memes or personal photos into the distinct style of Ghibli founder Hayao Miyazaki.
But the trend also highl
Debug <class 'scraipe.extended.news_scraper.NewsScraper'>[SUCCESS]

=== Non-News Link ===
Content: Example Domain
Example Domain
This domain is for use in illustrative examples in documents. You may use this
    domain in literature without prior coordination or asking for permission.
More information...
Debug: <class 'scraipe.defaults.text_scraper.TextScraper'>[SUCCESS]
```

## Tips

- Test each custom scraper in isolation before integrating it with `MultiScraper`.
- Enable error preservation during development to capture and debug failure chains.
- Leverage [built-in scrapers](../get_started/bundled_components.md) provided by Scraipe.
- Extend `IScraper` or `IAsyncScraper` to implement your [custom scraping logic](./custom_components.md).
- Plug your`MultiScraper` into [a workflow](../get_started/basic_workflow.md) for bulk scraping and analysis.