_AVAILABLE = False
try:
    import telethon
    import trafilatura
    import openai
    import aiohttp
    _AVAILABLE = True
except ImportError:
    raise "Missing dependencies. Install with `pip install scraipe[extended]`."

if _AVAILABLE:
    from scraipe.extended.telegram_message_scraper import TelegramMessageScraper
    from scraipe.extended.multi_scraper import MultiScraper
    from scraipe.extended.news_scraper import NewsScraper
    from scraipe.extended.llm_analyzers import OpenAiAnalyzer