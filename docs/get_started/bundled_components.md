# Bundled Components
Scraipe comes with a collection of powerful scrapers and analyzers that will keep expanding. If you need more functionality, see [custom components](../advanced_usage/custom_components.md).


## Scrapers

- **[`TextScraper`][scraipe.defaults.TextScraper]**: Extracts visible text from HTML content using `aiohttp` for fetching and `BeautifulSoup` for parsing.
- **[`RawScraper`][scraipe.defaults.RawScraper]**: Retrieves unmodified website content using `aiohttp`.
- **[`MultiScraper^`][scraipe.defaults.multi_scraper.MultiScraper]**: Uses ingress rules to determine the appropriate scraper for a given URL.
- **[`TelegramMessageScraper^`][scraipe.extended.TelegramMessageScraper]**: Scrapes Telegram messages using the `telethon` library.
- **[`NewsScraper^`][scraipe.extended.NewsScraper]**: Extracts article content from webpages using `aiohttp` and `trafilatura`.
- **[`TelegramNewsScraper^`][scraipe.extended.TelegramNewsScraper]**: A specialized `MultiScraper` for handling Telegram and news links, with a fallback to `TextScraper`.

## Analyzers

- **[`TextStatsAnalyzer`][scraipe.defaults.TextStatsAnalyzer]**: Computes text statistics such as word count, character count, sentence count, and average word length.
- **[`OpenAiAnalyzer^`][scraipe.extended.llm_analyzers.OpenAiAnalyzer]**: Uses OpenAI's API to analyze content based on a provided instruction and optional schema validation.
- **[`GeminiAnalyzer^`][scraipe.extended.llm_analyzers.GeminiAnalyzer]**: Integrates Google Gemini's API to analyze content based on instruction and mandatory schema validation. 

<sub>Components with a caret^ require `scraipe[extended]`.</sub>

---

Plug these components into your [basic workflow](./basic_workflow.md).