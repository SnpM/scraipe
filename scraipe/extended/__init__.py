_AVAILABLE = False
try:
    import telethon
    import trafilatura
    import openai
    _AVAILABLE = True
except ImportError:
    raise "Missing dependencies. Install with `pip install scraipe[extras]`."

if _AVAILABLE:
    from scraipe.extras.telegram_scraper import TelegramScraper
    from scraipe.extras.multi_scraper import MultiScraper
    from scraipe.extras.news_scraper import NewsScraper
    from scraipe.extras.llm_analyzers import OpenAiAnalyzer