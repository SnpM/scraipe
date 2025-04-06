# Bundled Components
Scraipe features a powerful set of scrapers and analyzers that we are continuously expanding.

Components with a caret^ require dependencies in the `scraipe[extended]` subpackage.

## Scrapers

- **[`TextScraper`][scraipe.defaults.TextScraper]**: Extracts visible text from HTML content using `aiohttp` for fetching and `BeautifulSoup` for parsing.
- **[`RawScraper`][scraipe.defaults.RawScraper]**: Retrieves raw webpage content as plain text using `aiohttp`.
- **[`MultiScraper^`][scraipe.defaults.multi_scraper.MultiScraper]**: Uses multiple ingress rules to determine the appropriate scraper for a given URL.
- **[`TelegramMessageScraper^`][scraipe.extended.TelegramMessageScraper]**: Scrapes Telegram messages using the `pyrogram` library.
- **[`NewsScraper^`][scraipe.extended.NewsScraper]**: Extracts article content from webpages using `aiohttp` and `trafilatura`.
- **[`TelegramNewsScraper^`][scraipe.extended.TelegramNewsScraper]**: A specialized `MultiScraper` for handling Telegram and news links, with fallback to `TextScraper`.

## Analyzers

- **[`TextStatsAnalyzer^`][scraipe.defaults.TextStatsAnalyzer]**: Computes text statistics such as word count, character count, sentence count, and average word length.
- **[`OpenAiAnalyzer^`][scraipe.extended.OpenAiAnalyzer]**: Uses OpenAI's API to analyze content based on a provided instruction and optional schema validation.

---

These scrapers and analyzers can be swapped into your [basic workflow](./basic_workflow.md).