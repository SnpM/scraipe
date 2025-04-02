_AVAILABLE = False
try:
    import telethon
    import trafilatura
    _AVAILABLE = True
except ImportError:
    "Missing dependencies. Install with `pip install scraipe[extras]`."

if _AVAILABLE:
    from scraipe.extras.telegram_scraper import TelegramScraper
    from scraipe.extras.multi_scraper import MultiScraper
    from scraipe.extras.news_scraper import NewsScraper
    
    from scraipe.extras.openai_analyzer import OpenAiAnalyzer