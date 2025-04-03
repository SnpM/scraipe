from abc import abstractmethod, ABC
from scraipe.classes import IScraper, ScrapeResult
import asyncio
from typing import final, Any, Callable, Awaitable, List
import threading
from concurrent.futures import Future, ThreadPoolExecutor
import nest_asyncio
# Base interface for asynchronous executors.
class IAsyncExecutor:
    def run(self, async_func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        raise NotImplementedError
    
    def shutdown(self, wait: bool = True) -> None:
        pass

@final
class MainThreadExecutor(IAsyncExecutor):
    """Run a function in the current thread with an asyncio event loop.
    
    Uses nest_asyncio to allow running coroutines in environments like Jupyter.
    """
    def run(self, async_func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        coro = async_func(*args, **kwargs)
        try:
            # Attempt to get the current running event loop.
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Patch the current loop to allow nested run_until_complete calls.
            nest_asyncio.apply(loop)
            return loop.run_until_complete(coro)
        else:
            return asyncio.run(coro)
@final
class BackgroundLoopExecutor(IAsyncExecutor):
    """Run a function using a pool of persistent background event loops.

    Each event loop runs in its own dedicated thread, and tasks are dispatched
    in a round-robin fashion. This avoids the overhead of creating a new event loop
    for every task.
    """
    def __init__(self, num_loops: int = 1) -> None:
        self.num_loops = num_loops
        self.event_loops: List[asyncio.AbstractEventLoop] = []
        self.threads: List[threading.Thread] = []
        self._loop_index = 0
        self._lock = threading.Lock()
        for _ in range(num_loops):
            loop = asyncio.new_event_loop()
            t = threading.Thread(target=self._start_loop, args=(loop,), daemon=True)
            t.start()
            self.event_loops.append(loop)
            self.threads.append(t)

    def _start_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Set and run the event loop in the background thread."""
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def run(self, async_func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        """Dispatch the asynchronous function to one of the pooled event loops."""
        with self._lock:
            # Round-robin selection of the event loop
            loop = self.event_loops[self._loop_index]
            self._loop_index = (self._loop_index + 1) % self.num_loops
        
        coro = async_func(*args, **kwargs)
        # Schedule the coroutine to run in the selected loop
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        return future.result()

    def shutdown(self, wait: bool = True) -> None:
        """Shut down all event loops and join their threads."""
        for loop in self.event_loops:
            loop.call_soon_threadsafe(loop.stop)
        if wait:
            for t in self.threads:
                t.join()
                
class AsyncManager:
    """
    A static manager for asynchronous execution.
    
    By default, it uses MainThreadExecutor. To enable multithreading,
    call enable_multithreading() to switch to multithreaded event loops.
    """
    _executor: IAsyncExecutor = MainThreadExecutor()

    @staticmethod
    def run(async_func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        """
        Run the given asynchronous function using the underlying executor.
        """
        return AsyncManager._executor.run(async_func, *args, **kwargs)

    @staticmethod
    def set_executor(executor: IAsyncExecutor) -> None:
        """
        Replace the current executor with a new one.
        """
        AsyncManager._executor = executor

    @staticmethod
    def enable_multithreading(max_workers: int = 1) -> None:
        """
        Switch to a multithreaded executor. Tasks will then be dispatched to background threads.
        """
        # Shut down the current executor if it's a BackgroundLoopExecutor
        AsyncManager._executor.shutdown(wait=True)
        # Create a new BackgroundLoopExecutor with the specified number of workers
        AsyncManager._executor = BackgroundLoopExecutor(max_workers)
    
    @staticmethod
    def disable_multithreading() -> None:
        """
        Switch back to the main thread executor.
        """
        # Shut down the current executor if it's a BackgroundLoopExecutor
        AsyncManager._executor.shutdown(wait=True)
        # Create a new MainThreadExecutor
        AsyncManager._executor = MainThreadExecutor()