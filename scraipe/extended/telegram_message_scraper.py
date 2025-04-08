from scraipe.classes import IScraper, ScrapeResult
import requests
from bs4 import BeautifulSoup
from pyrogram import Client
import re
from scraipe.async_classes import IAsyncScraper
from scraipe.async_util import AsyncManager
import warnings

class TelegramMessageScraper(IAsyncScraper):
    """
    A scraper that uses the pyrogram library to pull the contents of Telegram messages.

    Attributes:
        name (str): The name for the client session.
        api_id (str): The API ID for the Telegram client.
        api_hash (str): The API hash for the Telegram client.
        phone_number (str): The phone number associated with the Telegram account.
    """
        
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

    def __init__(self, name: str, api_id: str, api_hash: str, phone_number: str):
        """
        Initialize the TelegramMessageScraper with necessary connection parameters.

        Parameters:
            name (str): The name for the session.
            api_id (str): The Telegram API ID.
            api_hash (str): The Telegram API hash.
            phone_number (str): The phone number for authentication.
        """
        self.name = name
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        
        print(f"Initializing the Telegram session...")
        self.authenticate()
    
    def authenticate(self) -> bool:
        """
        Authenticate the Telegram session and return whether the authentication was successful.
        """
        async def _authenticate():
            try:
                client = Client(self.name, api_id=self.api_id, api_hash=self.api_hash, phone_number=self.phone_number)
                if not await client.connect():
                    warnings.warn("Interactive login is required")
                    await client.start()
                await client.stop()
            except:
                return False
            else:
                return True
        
        return AsyncManager.run(_authenticate())
        
    def get_expected_link_format(self):
        # regex for telegram message links
        return "https://t.me/[^/]+/[0-9]+"

    async def _get_telegram_content(self, chat_name: str, message_id: int):
        """
        Retrieve the content of a Telegram message asynchronously.

        Parameters:
            chat_name (str): The username or ID of the chat.
            message_id (int): The ID of the message to retrieve.

        Returns:
            str: The text or caption of the Telegram message.

        Raises:
            Exception: If failing to retrieve the chat or message, or if the chat is restricted.
        """
        client = Client(self.name, api_id=self.api_id, api_hash=self.api_hash, phone_number=self.phone_number)
        authenticated = await client.connect()
        if not authenticated:
            raise Exception("Telagram session not auth'd. Please authenticate by calling authenticate().")
    
        try:
            entity = await client.get_chat(chat_name)
        except Exception as e:
            raise Exception(f"Failed to get chat for {chat_name}: {e}")
        if hasattr(entity, 'restricted') and entity.restricted:
            raise Exception(f"Chat {chat_name} is restricted.")
        try:
            message = await client.get_messages(entity.id, message_id)
        except Exception as e:
            raise Exception(f"Failed to get message {message_id} from {chat_name}: {e}")
        
        content = None
        if message:
            content = message.text or message.caption
        assert content is not None, f"Message {message_id} from {chat_name} is None."
        
        await client.disconnect()
        return content

    async def async_scrape(self, url: str) -> ScrapeResult:
        """
        Asynchronously scrape the content of a Telegram message from a URL.

        Parameters:
            url (str): A URL formatted as 'https://t.me/{username}/{message_id}'.

        Returns:
            ScrapeResult: An object representing the success or failure of the scraping process.

        The method validates the URL, extracts the username and message ID, and retrieves the message content.
        """
        if not url.startswith("https://t.me/"):
            return ScrapeResult(link=url, scrape_success=False, scrape_error=f"URL {url} is not a telegram link.")
        match = re.match(r"https://t.me/([^/]+)/(\d+)", url)
        if not match:
            error = f"Failed to extract username and message id from {url}"
            return ScrapeResult.fail(url, error)
        username, message_id = match.groups()
        try:
            message_id = int(message_id)
        except ValueError:
            error = f"Message ID {message_id} is not a valid integer."
            return ScrapeResult.fail(url, error)
        try:
            content = await self._get_telegram_content(username, message_id)
            assert content is not None, f"Message {message_id} from {username} is None."
        except Exception as e:
            return ScrapeResult.fail(url, f"Failed to scrape {url}. Error: {e}")
        return ScrapeResult.succeed(url, content)

    def disconnect(self):
        """
        Disconnect any active sessions or clean up resources.

        Note:
            This method is currently a placeholder with no implemented disconnect logic.
        """
        pass