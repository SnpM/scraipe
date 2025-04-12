import telethon.client
import telethon.sessions
from scraipe.classes import IScraper, ScrapeResult
import requests
from bs4 import BeautifulSoup
import re
from scraipe.async_classes import IAsyncScraper
from scraipe.async_util import AsyncManager
import warnings

from telethon import TelegramClient
from telethon.sessions import StringSession, SQLiteSession
from threading import Lock
import telethon

import logging
from sqlite3 import OperationalError
import asyncio
import time
import qrcode
import threading
from enum import Enum
class AuthPhase(Enum):
    NOT_STARTED = 0
    AUTHENTICATED = 1
    FAILED = -1
    AUTH_CODE_SENT = -2
    NEED_PASSWORD = -3
    MONITORING_QR = -4

class TelegramMessageScraper(IAsyncScraper):
    """
    A scraper that uses the telethon library to pull the contents of Telegram messages.

    Attributes:
        api_id (str): The API ID for the Telegram client.
        api_hash (str): The API hash for the Telegram client.
        phone_number (str): The phone number associated with the Telegram account.

    """

    qr_login:telethon.custom.QRLogin
    
    def __init__(self, api_id: str, api_hash: str, phone_number: str = None, session_name:str = None, password=None, sync_auth: bool = True, use_qr_login: bool = False):
        """
        Initialize the TelegramMessageScraper with necessary connection parameters.

        Parameters:
            api_id (str): The Telegram API ID.
            api_hash (str): The Telegram API hash.
            phone_number (str): The phone number for authentication.
            session_name (str): The name of the session. If None, a temporary StringSesssion will be used 
        """
        self.session_name = session_name
        self.session_string = None
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.session_lock = Lock()
        self.login_token = None
        self.qr_login = None
        self.password = password
        self.use_qr_login = use_qr_login
        self.qr_login_listeners = None
        
        if not self.use_qr_login:
            assert self.phone_number is not None, "phone_number is None. Please provide a phone number for authentication."
        
        logging.info(f"Initializing the Telegram session...")
        authd = self.authenticate(sync_auth=sync_auth, use_qrcode=use_qr_login)
        if sync_auth and not authd:
            raise RuntimeError("Failed to authenticate the Telegram session. Please check your credentials.")
    
    def save_session(self, client:TelegramClient):
        with self.session_lock:
            # Serialize a session for creating new clients
            self.session_string = StringSession.save(client.session)
    
    def try_get_session_client(self) -> TelegramClient:
        try:
            client = TelegramClient(self.session_name, api_id=self.api_id, api_hash=self.api_hash)
        except Exception as e:
            logging.warning(f"Failed to acquire SQLite session. Creating a temporary StringSession.")
            client = TelegramClient(StringSession(), api_id=self.api_id, api_hash=self.api_hash)
        return client
    
    def is_authenticated(self) -> bool:
        return self.session_string is not None
    
    def is_monitoring_qr(self) -> bool:
        return self._qr_login_lock.locked()
    
    _qr_login_lock:threading.Lock = threading.Lock()    
    async def _qr_login_loop(self,
        qr_login: telethon.custom.QRLogin, client: TelegramClient) -> AuthPhase:
        
        acquired = self._qr_login_lock.acquire(blocking=False)
        if not acquired:
            raise RuntimeError("QR login loop is already running. Cannot start a new one.")
    
        # ASsume client is already connected to generate the QR code
        assert qr_login is not None
        assert client is not None
        if not await client.is_user_authorized():

            # wait until qr_login expires
            expire_time = qr_login.expires
            timeout = expire_time.timestamp() - time.time()
            try:
                r = await qr_login.wait(timeout=timeout)
            except TimeoutError as e:
                logging.warning("QR code login timed out.")
                result = AuthPhase.FAILED
            else:
                if r:
                    logging.info("Successfully authenticated with QR code.")
                    self.save_session(client)
                    result = AuthPhase.AUTHENTICATED
                else:
                    logging.warning("QR code authentication failed.")
                    result = AuthPhase.FAILED
        else:
            result = AuthPhase.AUTHENTICATED
            
        print ("calling callbacks...",self.is_authenticated())
        for cb in self.qr_login_listeners:
            cb(result)
        self.qr_login = None
        self.qr_login_listeners = None
        self._qr_login_lock.release()
        return result
    
    async def _sign_in_with_code(self,
        code: str, client:TelegramClient, phone_number: str,
        login_token: str = None, password: str = None) -> AuthPhase:
        
        password = None if self.password == "" else self.password
        login_token = login_token if login_token else self.login_token
        
        if login_token is None:
            raise RuntimeError("login_token is None. Please call authenticate() first.")
                
        if client is None:
            client = self.try_get_session_client()
            
        await client.connect()
        if not await client.is_user_authorized():
            is_authed = False
            try:
                sign_in_result = await client.sign_in(phone=phone_number, code=code, phone_code_hash=login_token, password=password)
                is_authd = await client.is_user_authorized()
            except telethon.errors.SessionPasswordNeededError as e:
                if password is None:
                    logging.warning("Two-factor authentication is enabled. Please configure password.")    
                    return AuthPhase.NEED_PASSWORD
                assert False         
            finally:
                client.disconnect()

            if is_authd:
                self.save_session(client)
                logging.info("Successfully authenticated.")
                return AuthPhase.AUTHENTICATED
            else:
                logging.warning("Failed to authenticate. Please check your credentials.")
                return AuthPhase.FAILED
                
        else:
            logging.info("Already authenticated. No need to sign in.")
            return AuthPhase.AUTHENTICATED
    
    def sign_in(self, code: str = None, client:TelegramClient=None) -> AuthPhase:
        """
        Sign in to the Telegram account using the provided auth code.

        Parameters:
            phone_number (str): The phone number associated with the account.
            code (str): The verification code sent to the phone number.

        Raises:
            telethon.errors.SessionPasswordNeededError: If two-factor authentication is enabled and no password is provided.
        """
        assert self.login_token is not None, "login_token is None. Please call authenticate() first."
        return AsyncManager.get_executor().run(self._sign_in_with_code(code, client, self.phone_number, self.login_token, self.password))
    
    def get_qr_url(self) -> str:
        assert self.use_qr_login, "QR code login is not enabled. Please set use_qr_login=True in the constructor."
        assert self.qr_login is not None, "qr_login is None. Please call authenticate() first."
        return self.qr_login.url
    
    def subscribe_qr_login_listener(self, callback):
        """
        Subscribe a callback that receives AuthPhase updates
        during the QR login process.
        """
        self.qr_login_listeners.append(callback)
    
    def authenticate(self, sync_auth = True, use_qrcode = False) -> AuthPhase:
        """
        Authenticate the Telegram session and return whether the authentication was successful.
        
        Returns:
            
        """
        async def _authenticate() -> AuthPhase:
            self.login_token = None
            is_authd = False

            try:
                client = self.try_get_session_client()
                
                await client.connect()
                if await client.is_user_authorized():
                    logging.info("Already authenticated. No need to authenticate again.")
                    is_authd = True
                else:
                    if use_qrcode:
                        # Use QR code authentication
                        logging.info("Using QR code authentication.")
                        self.qr_login = await client.qr_login()
                        # Clear listeners
                        self.qr_login_listeners = []
                    
                        if sync_auth:
                            # Direct user to scan the QR code online
                            url = self.qr_login.url
                            qr = qrcode.QRCode()
                            qr.add_data(url)
                            qr.make(fit=True)
                            print("Please scan the QR code from the Telegram app:")
                            qr.print_ascii()
                            result = await self._qr_login_loop(self.qr_login, client)
                            is_authd = result == AuthPhase.AUTHENTICATED
                        else:
                            logging.info("Starting QR code authentication monitoring.")
                            asyncio.create_task(self._qr_login_loop(self.qr_login, client))
                            return AuthPhase.MONITORING_QR
                    else:
                        sent = await client.send_code_request(phone=self.phone_number)
                        login_token = sent.phone_code_hash
                        self.login_token = login_token
                        print("Sent code request", login_token, sent)

                        if sync_auth:
                            # get input from user and sign in immediately
                            code = input("Enter the code you received: ")
                            await self._sign_in_with_code(self.phone_number, code, login_token, client)
                    is_authd = await client.is_user_authorized()
                await client.disconnect()
            except Exception as e:
                import traceback
                traceback.print_exc()
                logging.error(f"Failed to authenticate due to exception: {e}")
                return AuthPhase.FAILED
            else:
                if is_authd: 
                    self.save_session(client)
                    return AuthPhase.AUTHENTICATED
                else:
                    if self.login_token:
                        return AuthPhase.AUTH_CODE_SENT
                    else:
                        return AuthPhase.FAILED
        return AsyncManager._executor.run(_authenticate())
        
        
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
        assert self.session_string is not None, "Session is None. Please authenticate first."
        client = TelegramClient(StringSession(self.session_string), api_id=self.api_id, api_hash=self.api_hash)
        await client.connect()
        if not await client.is_user_authorized():
            raise Exception("Telagram session not auth'd. Please authenticate by calling authenticate().")        
        async with client:        
            # Get chat
            try:
                entity = await client.get_entity(chat_name)
            except Exception as e:
                raise Exception(f"Failed to get chat for {chat_name}: {e}")
            if hasattr(entity, 'restricted') and entity.restricted:
                raise Exception(f"Chat {chat_name} is restricted.")
            
            # get message
            try:
                message = await client.get_messages(entity,ids=message_id)
            except Exception as e:
                raise Exception(f"Failed to get message {message_id} from {chat_name}: {e}")
            
            # Extract content
            if message is None:
                raise Exception(f"Message {message_id} from {chat_name} is None.")
            if message.message is not None:
                content = message.message
            else:
                raise Exception(f"Message {message_id} from {chat_name} is None.")
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
            return ScrapeResult.fail(url, f"Failed to scrape due to exception: {e}")
        return ScrapeResult.succeed(url, content)

    def disconnect(self):
        """
        Disconnect any active sessions or clean up resources.

        Note:
            This method is currently a placeholder with no implemented disconnect logic.
        """
        pass