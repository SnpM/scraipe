_AVAILABLE = False
try:
    import telethon
    import trafilatura
    import openai
    _AVAILABLE = True
except ImportError:
    raise "Missing dependencies. Install with `pip install scraipe[extras]`."

if _AVAILABLE:
    from scraipe.extended.telegram_scraper import TelegramScraper
    from scraipe.extended.multi_scraper import MultiScraper
    from scraipe.extended.news_scraper import NewsScraper
    from scraipe.extended.llm_analyzers import OpenAiAnalyzer