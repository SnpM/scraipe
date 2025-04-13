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
from telethon.sessions import StringSession
from threading import Lock
import telethon
import os
import logging
import asyncio
import time
import qrcode
import threading
from enum import Enum
from threading import Event
from scraipe.common import AtomicInteger

from filelock import FileLock
from queue import Queue
from abc import ABC, abstractmethod
from telethon.custom import QRLogin

from typing import List, Callable, final, Any, cast, AsyncContextManager
class AuthState(Enum):
    NOT_STARTED = 0
    WORKING = -1
    AUTHENTICATED = 1
    FAILED = -100

class LoginType(Enum):
    AuthCode = 1
    QRCode = 2
    

    
class ILoginContext(ABC):
    
    # Attributes
    _client: TelegramClient
    __done_lock:Lock
    __done_listeners: List[Callable[[AuthState], None]]
    __done_event:Event
    __session_string: str
    __auth_state: AuthState
    @property
    def auth_state(self) -> AuthState:
        """Get the current authentication state."""
        return self.__auth_state
    
    def __init__(self, client: TelegramClient, is_sync = True):
        """
        Initialize the login context with a Telegram client.
        After passing the client, do not use it anymore.
        The client will be disconnected when the login process is done.
        Args:
            client (TelegramClient): The fresh Telegram client to use for authentication.
            sync (bool): If True, the starting the login process will wait for the authentication to complete.
        """
        
        self._client = client
        self.__done_listeners = []
        self.__done_event = Event()
        self.__done_lock = Lock()
        self.__auth_state = AuthState.NOT_STARTED
        self.__is_sync = is_sync
        
        self.__session_string = None

        assert isinstance(self._client, TelegramClient), "client is not a TelegramClient instance."
        assert self._client.is_connected() == False, "Expecting a fresh client. The client should not be connected."
    def get_session_string(self):
        """
        Get the session string for the authenticated session.
        """
        assert self.__auth_state == AuthState.AUTHENTICATED, "Session is not authenticated."
        assert self.__session_string is not None, "Session is None."
        return self.__session_string
    
    def __save_session(self):
        # Serialize a session for creating new clients
        self.__session_string = StringSession.save(self._client.session)
    
    @final
    def __done(self, auth_state: AuthState):
        """
        Mark the QR login process as done and notify listeners.
        Also save the session if authenticated.
        Disconnects and clears the client.
        """
        
        with self.__done_lock:            
            if self.__done_event.is_set():
                raise RuntimeError("Login process is already done.")
            
            self.__auth_state = auth_state
            
            for listener in self.__done_listeners:
                listener(auth_state)

            # Clean up listeners
            self.__done_listeners = None
            
            if auth_state == AuthState.AUTHENTICATED:
                self.__save_session()
                logging.info("Session saved.")
            
            # Clean up client
            self._client = None
            self.__done_event.set()

    @final
    def subscribe_done(self, callback: Callable[[AuthState], None]):
        """
        Subscribe a callback that gets called when the login process is done.
        This callback will be run on the background thread monitoring the login process.
        If the login process is already done, the callback will be called immediately (sync).
        """
        with self.__done_lock:
            if self.__done_event.is_set():
                callback(self.__auth_state)
            else:
                self.__done_listeners.append(callback)
    
    @final
    def is_done(self) -> bool:
        return self.__done_event.is_set()
    
    @final
    async def run(self) -> AuthState:
        """
        Orchestrates the login process.
        """
        # connect the client
        connected = False
        try:
            await self._client.connect()
            connected = self._client.is_connected()
        except Exception as e:
            logging.error(f"Failed to connect to Telegram client: {e}")
            pass
        assert connected, "Should be connected to Telegram client by now."
        
        # Check if already authorized
        authorized = await self._client.is_user_authorized()
        if authorized:
            logging.info("Client already authd.")
            self.__done(AuthState.AUTHENTICATED)
            return self.__auth_state
        
        # Start the login process
        self.__auth_state = await self._start()
        
        if self.__auth_state == AuthState.WORKING:
            # Start monitoring; monitoring will notify done by itself
            if self.__is_sync:
                # Run sync logic and wait for completion
                self.__auth_state = await self._on_sync()
                self.__auth_state = await self.monitor()
            else:
                # Start the monitoring loop in the background
                asyncio.create_task(self.monitor())
                self.__auth_state = AuthState.WORKING
        else:
            # No need to monitor
            self.__done(self.__auth_state)
            
        return self.__auth_state
        
    @final
    async def monitor(self) -> AuthState:
        """
        Orchestrate monitoring the login process.
        
        Returns:
            AuthState: The final authentication state.
        """
        if self.is_done():
            raise RuntimeError("Login process is already done.")
        auth_state = await self._monitor()
        self.__done(auth_state)
        return auth_state
    
    @abstractmethod
    async def _start(self) -> AuthState:
        """
        Start the login process.
        This method should be overridden by subclasses to implement specific login logic.
        
        Returns:
            AuthState: The initial authentication state.
        """        
        pass
    
    @abstractmethod
    async def _on_sync(self) -> None:
        """
        Execute logic for synchronous sign in. This could involve drawing a QR code or waiting for user input.
        Processing logic should still be included in _on_monitor() method.
        This method should be implemented by subclasses to provide specific synchronous logic.
        """
        pass
    @abstractmethod
    async def _monitor(self) -> AuthState:
        """
        Monitor the login process and return the authentication state.
        This method should be implemented by subclasses to provide specific monitoring logic.
        
        Returns:
            AuthState: The final authentication state.
        """
        pass
            

class QrLoginContext(ILoginContext):
    
    qr_login: QRLogin = None
    
    def __init__(self, client: TelegramClient, is_sync:bool):
        super().__init__(client, is_sync)
        
    def get_qr_url(self) -> str:
        """
        Get the URL for the QR code login.
        """
        assert isinstance(self.qr_login, QRLogin), "qr_login is not a QRLogin instance."
        return self.qr_login.url
    
    async def _start(self) -> AuthState:
        logging.info("Using QR code authentication.")
        self.qr_login = await self._client.qr_login()
        return AuthState.WORKING
    
    async def _on_sync(self):
        url = self.qr_login.url
        qr = qrcode.QRCode()
        qr.add_data(url)
        qr.make(fit=True)
        # Direct user to scan the QR code online
        print("Please scan the QR code from the Telegram app:")
        qr.print_ascii()
    
    async def _monitor(self) -> AuthState:
        qr_login = self.qr_login
        client = self._client
    
        # Assume client is already connected to generate the QR code
        assert qr_login is not None
        assert client is not None
        if not await client.is_user_authorized():
            # timeout when qr_login expires
            expire_time = qr_login.expires
            timeout = expire_time.timestamp() - time.time()
            try:
                r = await qr_login.wait(timeout=timeout)
            except TimeoutError as e:
                logging.error("QR code login timed out.")
                auth_state = AuthState.FAILED
            else:
                if r:
                    logging.info("Successfully authenticated with QR code.")
                    auth_state = AuthState.AUTHENTICATED
                else:
                    logging.warning("QR code authentication failed.")
                    auth_state = AuthState.FAILED
        else:
            auth_state = AuthState.AUTHENTICATED
            
        return auth_state
    
class AuthCodeLoginContext(ILoginContext):
    phone_number:str
    __auth_code_queue:Queue[str]
    login_token:str
    timeout:float
    def __init__(self, client: TelegramClient, is_sync:bool, phone_number: str, password:str=None, timeout:float=120):
        super().__init__(client, is_sync)
        self.phone_number = phone_number
        self.__auth_code_queue = Queue()
        self.timeout = timeout
        
    def push_auth_code(self, auth_code: str):
        """
        Push the authentication code to the auth code login process.
        """
        self.__auth_code_queue.put(auth_code)
        
    async def __sign_in(self,
        code: str, client:TelegramClient, phone_number: str,
        login_token: str = None, password: str = None) -> AuthState:
        client = self._client

        sign_in_result = await client.sign_in(phone=phone_number, code=code, phone_code_hash=login_token, password=password)
        if isinstance(sign_in_result, telethon.types.User):
            sign_in_result: telethon.types.User
            return AuthState.AUTHENTICATED
        else:
            sign_in_result: telethon.types.auth.SentCode            
            logging.error("Failed to sign in.", sign_in_result)
            return AuthState.FAILED
                    
    async def _start(self) -> AuthState:
        sent = await self._client.send_code_request(phone=self.phone_number)
        login_token = sent.phone_code_hash
        self.login_token = login_token
        logging.info("Sent code request, stored token:", login_token)
        return AuthState.WORKING
        
    async def _on_sync(self):
        # Get auth code from user in console
        auth_code = input("Enter the code you received: ")
        self.push_auth_code(auth_code)
        
    async def _monitor(self):
        # Wait for the monitoring loop to indicate completion
        POLL_INTERVAL = .4
        expire_time = 120
        acc = 0
        while True:
            if not self.__auth_code_queue.empty():
                auth_code = self.__auth_code_queue.get()
                try:
                    return await self.__sign_in(phone=self.phone_number, code=auth_code)
                except telethon.errors.SessionPasswordNeededError as e:
                    logging.error("Two-factor authentication is enabled. Please configure password.")
                    return AuthState.FAILED
                except Exception as e:
                    logging.error(f"Failed to authenticate with auth code: {e}")
                    return AuthState.FAILED
            
            if acc >= expire_time:
                logging.warning("Authentication timed out.")
                return AuthState.FAILED
                
            await asyncio.sleep(POLL_INTERVAL)
            acc += POLL_INTERVAL
            

class TelegramMessageScraper(IAsyncScraper):
    """
    A scraper that uses the telethon library to pull the contents of Telegram messages.

    Attributes:
        api_id (str): The API ID for the Telegram client.
        api_hash (str): The API hash for the Telegram client.
        phone_number (str): The phone number associated with the Telegram account.

    """

    login_context: ILoginContext
    def __init__(self,
        api_id: str, api_hash: str,
        phone_number: str = None, session_name:str = None, password=None,
        sync_auth: bool = True, login_type: LoginType = LoginType.QRCode, defer_auth = False):
        """
        Initialize the TelegramMessageScraper with necessary connection parameters.

        Parameters:
            api_id (str): The Telegram API ID.
            api_hash (str): The Telegram API hash.
            phone_number (str): The phone number for authentication.
            session_name (str): The name of the session. If None, a temporary StringSesssion will be used 
            password (str): The password for two-factor authentication.
            sync_auth (bool): If True, the authentication process will be synchronous.
            login_type (LoginType): The type of login to use (QRCode or AuthCode).
            defer_auth (bool): If True, the scraper will be initialized without authentication.
        """
        self.session_name = session_name
        self.session_string = None
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.password = password
        self.login_type = login_type
        self.sync_auth = sync_auth
        
        self.login_token = None
        self.login_context = None
        
        self.__session_file_version = AtomicInteger()
        
        if defer_auth:
            return
        
        logging.info(f"Initializing the Telegram session...")
        auth_state = self.authenticate(login_type=login_type, sync_auth=sync_auth)
        
        # Detect failure
        if sync_auth and auth_state != AuthState.AUTHENTICATED:
            raise RuntimeError("Failed to synchronously authenticate the Telegram session.")
        if auth_state == AuthState.FAILED:
            raise RuntimeError("Login process failed")
    
    class ClientConnection(AsyncContextManager[TelegramClient]):
        """
        Context manager for connecting->disconnecting a new Telegram client.
        """
        def __init__(self, client:TelegramClient, client_lock: Lock = None):
            self.client = client
            self.client_lock = client_lock
        
        async def __aenter__(self):
            if self.client_lock is not None:
                if not self.client_lock.acquire(blocking=False):
                    raise RuntimeError("Failed to acquire client's lock.")
            await self.client.connect()
            return self.client
        
        async def __aexit__(self, exc_type, exc_value, traceback):
            await self.client.disconnect()
            if self.client_lock is not None:
                self.client_lock.release()
    
    __session_file_version:AtomicInteger
    def update_session_file(self, session_name: str, session_string: str, file_version:int):
        """
        Update the session file with the given session string.
        """
        assert isinstance(session_name, str), "session_name must be a string."
        assert isinstance(session_string, str), "session_string must be a string."
        if file_version < self.__session_file_version.get():
            logging.warning("Session file version is lower is stale. Ignoring.")
            return
        
        lock_path = self.get_session_filename(session_name) + ".lock"
        with FileLock(lock_path):
            # Write the session string to the file
            with open(self.get_session_filename(session_name), 'w') as f:
                f.write(session_string)
                logging.info(f"Session string saved to {session_name}")
            
    def load_session_file(self, session_name: str) -> str:
        """
        Load the session string from the given session file.
        """
        assert isinstance(session_name, str), "session_name must be a string."
        
        session_filename = self.get_session_filename(session_name)
        if not os.path.exists(session_filename):
            logging.warning(f"Session file {session_name} does not exist.")
            return None
        
        lock_path = session_filename + ".lock"
        with FileLock(lock_path):
            # Read the session string from the file
            with open(session_filename, 'r') as f:
                session_string = f.read()
                logging.info(f"Session string loaded from {session_name}")
                return session_string
            
    
                
    def get_session_filename(self, session_name: str) -> str:
        """
        Get the session filename for the given session name.
        """
        EXTENSION = ".session.txt"
        # If extension is not present, add it
        if not session_name.endswith(EXTENSION):
            session_name = session_name + EXTENSION
        return session_name
                
    def _new_client(self) -> TelegramClient:
        """
        Get a new Telegram client based on an existing session or a blank session.
        """
        client:TelegramClient = None
        string_session = None
        if isinstance(self.session_name, str):
            # Get new client from file associated with session_name
            
            session_string:str = None
            try:
                session_string = self.load_session_file(self.session_name)
                if session_string is None:
                    logging.info(f"Session {self.session_name} does not exist. Creating a new session.")
            except Exception as e:
                logging.error(f"Failed to read session file for {self.session_name}: {e}")

            # Parse the session string with StringSession
            if session_string is not None:
                try:
                    string_session = StringSession(session_string)
                except Exception as e:
                    raise (f"Session {self.session_name} may be corrupted.") from e

        if string_session is None:
            logging.info(f"Creating a blank session")
            string_session = StringSession()
            
        client = TelegramClient(session=string_session, api_id=self.api_id, api_hash=self.api_hash)
        return client
                
    def _authenticated_client(self) -> TelegramClient:
        """
        Get a new Telegram client with the authenticated session.
        """
        assert self.login_context is not None, "login_context is None. Please call authenticate() first."
        assert self.login_context.auth_state == AuthState.AUTHENTICATED, "login_context is not authenticated."
        
        # Get the serialized auth'd session
        session_str = self.login_context.get_session_string()
        # Create a new client with the session string
        client = TelegramClient(StringSession(session_str), api_id=self.api_id, api_hash=self.api_hash)
        
        return client
    
    def is_authenticating(self) -> bool:
        """
        Check if the client is currently authenticating.
        """
        return self.login_context is not None and self.login_context.auth_state == AuthState.WORKING
    
    def is_authenticated(self) -> bool:
        return self.login_context is not None and self.login_context.auth_state == AuthState.AUTHENTICATED
    
    async def _requires_interaction(self) -> bool:
        client = self._new_client()
        async with self.ClientConnection(client):
            if not await client.is_user_authorized():
                return True
        return False
    
    def requires_interaction(self) -> bool:
        """
        Check if the client requires user interaction for authentication.
        
        Returns:
            bool: True if user interaction is required, False otherwise.
        """
        return AsyncManager._executor.run(self._requires_interaction())
    
    def authenticate(self, login_type:LoginType=None, sync_auth:bool=None) -> AuthState:
        """
        Create a new login context and authenticate the user.
        
        Args:
            login_type (LoginType): The type of login to use (QRCode or AuthCode). If None, the instance's login_type will be used.
            sync_auth (bool): If True, the authentication process will be synchronous. If None, the instance's sync_auth will be used.
        """
        if login_type is None:
            login_type = self.login_type
        if sync_auth is None:
            sync_auth = self.sync_auth
        
        async def _authenticate() -> AuthState:
            client = self._new_client()
            # Pass control of client to the login context
            # In theory, we should not use the client anymore
            if login_type == LoginType.QRCode:
                self.login_context = QrLoginContext(client=client, is_sync=sync_auth)
            elif login_type == LoginType.AuthCode:
                self.login_context = AuthCodeLoginContext(
                    client=client,
                    phone_number=self.phone_number,
                    password= self.password)
            else:
                raise RuntimeError(f"Unknown login type: {login_type}")
            
            assert isinstance(self.login_context, ILoginContext), "login_context is not an instance of ILoginContext."

            # Start the login process
            auth_state = await self.login_context.run()
            cached_version:int = self.__session_file_version.increment_and_get()
            def on_done(auth_state: AuthState):
                # Save the session string to the file
                if auth_state == AuthState.AUTHENTICATED:
                    logging.info("Saving session string to file.")
                    session_string = self.login_context.get_session_string()
                    self.update_session_file(self.session_name, session_string, cached_version)
            if self.session_name is not None:
                self.login_context.subscribe_done(on_done)
            return auth_state
        return AsyncManager._executor.run(_authenticate())
        
        
    def get_expected_link_format(self):
        # regex for telegram message links
        return "https://t.me/[^/]+/[0-9]+"


    async def _get_telegram_content(self, chat_name: str, message_id: int) -> tuple[str,str]:
        """
        Retrieve the content of a Telegram message asynchronously.

        Parameters:
            chat_name (str): The username or ID of the chat.
            message_id (int): The ID of the message to retrieve.

        Returns:
            (str, str): A tuple containing the message content and an error message if any.

        Raises:
            Exception: If failing to retrieve the chat or message, or if the chat is restricted.
        """
        client = self._authenticated_client()
        async with self.ClientConnection(client):
            if not await client.is_user_authorized():
                return None, "Not authenticated."
            async with client:        
                # Get chat
                try:
                    entity = await client.get_entity(chat_name)
                except Exception as e:
                    return None, "Failed to get chat for {chat_name}"
                if hasattr(entity, 'restricted') and entity.restricted:
                    return None, f"Chat {chat_name} is restricted."
                
                # get message
                try:
                    message = await client.get_messages(entity,ids=message_id)
                except Exception as e:
                    return None, f"Failed to get message {message_id} from {chat_name}"
                
                # Extract content
                if message is None:
                    return None, f"Message {message_id} from {chat_name} is None."
                if message.message is not None:
                    content = message.message
                else:
                    return None, f"Message {message_id} from {chat_name} is empty."
                return content, None

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
            return ScrapeResult.fail(url, f"URL {url} is an invalid telegram message link.")
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
        
        content,err = await self._get_telegram_content(username, message_id)
        if err is not None:
            assert content is None, "Content should be None if there is an error."
            logging.error(f"Failed to scrape {url}: {err}")
            return ScrapeResult.fail(url, f"{err}")
        
        if content is None:
            return ScrapeResult.fail(url, f"Content is None.")
        return ScrapeResult.succeed(url, content)