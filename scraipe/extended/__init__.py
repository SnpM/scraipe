"""
The `extended` package provides additional scrapers and analyzers for advanced use cases.
It includes tools for scraping Telegram messages, news articles, and performing LLM-based analysis.
Dependencies for this package can be installed using `pip install scraipe[extended]`.
"""

_AVAILABLE = False
try:
    # Validate extemded dependencies from pyproject.toml:
    for pkg in ["telethon", "trafilatura"]:
        __import__(pkg)
    _AVAILABLE = True
except ImportError:
    raise "Missing dependencies. Install with `pip install scraipe[extended]`."

if _AVAILABLE:
    from scraipe.extended.telegram_message_scraper import TelegramMessageScraper
    from scraipe.extended.news_scraper import NewsScraper
    from scraipe.extended.telegram_news_scraper import TelegramNewsScraper
    from scraipe.extended.llm_analyzers import OpenAiAnalyzer
    from scraipe.extended.llm_analyzers import GeminiAnalyzer