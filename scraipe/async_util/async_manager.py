from scraipe.async_util.async_executors import DefaultBackgroundExecutor, EventLoopPoolExecutor
from scraipe.async_util.async_executors import IAsyncExecutor
import asyncio
from typing import final, Any, Awaitable, List, Generator, AsyncGenerator
from queue import Queue
from concurrent.futures import Future
import time

class AsyncManager:
    """
    A static manager for asynchronous execution in a synchronous context.
    
    By default, it uses MainThreadExecutor. To enable multithreading,
    call enable_multithreading() to switch to multithreaded event loops.
    """
    _executor: IAsyncExecutor = DefaultBackgroundExecutor()

    @staticmethod
    def get_executor() -> IAsyncExecutor:
        """
        Get the current executor used by AsyncManager.
        
        Returns:
            An object that implements the IAsyncExecutor interface.
        """
        return AsyncManager._executor

    @staticmethod
    def set_executor(executor: IAsyncExecutor) -> None:
        """
        Replace the current asynchronous executor used by AsyncManager with a new executor.
        
        Args:
            executor: An object that implements the IAsyncExecutor interface, responsible
                      for managing and executing asynchronous tasks.
        
        Returns:
            None.
        """
        AsyncManager._executor = executor

    @staticmethod
    def enable_multithreading(pool_size: int = 3) -> None:
        """
        Switch to a multithreaded executor. Tasks will then be dispatched to background threads.
        """
        # Shut down the current executor if it's a BackgroundLoopExecutor
        AsyncManager._executor.shutdown(wait=True)
        # Create a new BackgroundLoopExecutor with the specified number of workers
        AsyncManager._executor = EventLoopPoolExecutor(pool_size)
    
    @staticmethod
    def disable_multithreading() -> None:
        """
        Switch back to the main thread executor.
        """
        # Shut down the current executor if it's a BackgroundLoopExecutor
        AsyncManager._executor.shutdown(wait=True)
        # Create a new MainThreadExecutor
        AsyncManager._executor = DefaultBackgroundExecutor()