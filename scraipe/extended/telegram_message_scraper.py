from scraipe.classes import IScraper, ScrapeResult
import requests
from bs4 import BeautifulSoup
from pyrogram import Client
import re
from scraipe.async_classes import IAsyncScraper
from scraipe.async_util import AsyncManager

class TelegramMessageScraper(IAsyncScraper):
    """A scraper that uses the pyrogram library to pull the contents of telegram messages."""
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

    def __init__(self, name: str, api_id: str, api_hash: str, phone_number: str):
        # Removing the cached client and storing parameters instead
        self.name = name
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number

    async def _get_telegram_content(self, chat_name: str, message_id: int):
        async with Client(self.name, api_id=self.api_id, api_hash=self.api_hash, phone_number=self.phone_number) as client:
            # Search for chat instead of entity
            try:
                entity = await client.get_chat(chat_name)
            except Exception as e:
                raise Exception(f"Failed to get chat for {chat_name}: {e}")
            # Check if entity is restricted/unaccessible (if available)
            if hasattr(entity, 'restricted') and entity.restricted:
                raise Exception(f"Chat {chat_name} is restricted.")
            # Get the message from chat using chat id
            try:
                message = await client.get_messages(entity.id, message_id)
            except Exception as e:
                raise Exception(f"Failed to get message {message_id} from {chat_name}: {e}")
            
            # Look for content in text and caption
            content = None
            if message:
                content = message.text or message.caption
            assert content is not None, f"Message {message_id} from {chat_name} is None."
            
            return content

    async def async_scrape(self, url: str) -> ScrapeResult:
        if not url.startswith("https://t.me/"):
            return ScrapeResult(link=url, scrape_success=False, scrape_error=f"URL {url} is not a telegram link.")
        # Extract the username and message id
        match = re.match(r"https://t.me/([^/]+)/(\d+)", url)
        if not match:
            error = f"Failed to extract username and message id from {url}"
            return ScrapeResult.fail(url,error)
        username, message_id = match.groups()
        try:
            message_id = int(message_id)
        except ValueError:
            error = f"Message ID {message_id} is not a valid integer."
            return ScrapeResult.fail(url,error)
        
        # Run async function
        try:
            content = await self._get_telegram_content(username, message_id)
            assert content is not None, f"Message {message_id} from {username} is None."
        except Exception as e:
            return ScrapeResult.fail(url,f"Failed to scrape {url}. Error: {e}")
        
        return ScrapeResult.success(url, content)
    
        
    def disconnect(self):
        pass