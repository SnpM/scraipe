from abc import abstractmethod, ABC
from scraipe.classes import IScraper, ScrapeResult
import asyncio
from typing import final, Any, Callable, Awaitable, List, Generator, Tuple, AsyncGenerator
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from queue import Queue
import time
import nest_asyncio
# Base interface for asynchronous executors.
class IAsyncExecutor:
    @abstractmethod
    def run(self, async_func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        raise NotImplementedError
    
    @abstractmethod
    async def async_run(self, async_func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        raise NotImplementedError
    
    def shutdown(self, wait: bool = True) -> None:
        pass

@final
class DefaultThreadExecutor(IAsyncExecutor):
    """Run a function in the current thread with an asyncio event loop.
    Stateless executor that runs functions in the current thread.
    Uses nest_asyncio to allow running coroutines in environments like Jupyter.
    """
    def run(self, async_func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        assert isinstance(async_func, Callable), "async_func must be callable"
        assert asyncio.iscoroutinefunction(async_func), "async_func must be a coroutine function"
        
        coro = async_func(*args, **kwargs)
        loop = asyncio.get_event_loop()

        if loop.is_running():            
            # Patch the current loop to allow nested run_until_complete calls.
            nest_asyncio.apply(loop)
        return loop.run_until_complete(coro)

    async def async_run(self, async_func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        # Just run the function in the current thread.
        return await async_func(*args, **kwargs)

import asyncio
import threading
from concurrent.futures import Future
from typing import Any, Callable, Awaitable, List, Tuple

class EventLoopPoolExecutor:
    """
    A utility class that manages a pool of persistent asyncio event loops,
    each running in its own dedicated thread. It load balances tasks among
    the event loops by tracking pending tasks and selecting the loop with
    the smallest load.
    """
    def __init__(self, num_loops: int = 1) -> None:
        self.num_loops = num_loops
        self.event_loops: List[asyncio.AbstractEventLoop] = []
        self.threads: List[threading.Thread] = []
        # Track the number of pending tasks per event loop.
        self.pending_tasks: List[int] = [0] * num_loops
        self._lock = threading.Lock()

        for _ in range(num_loops):
            loop = asyncio.new_event_loop()
            t = threading.Thread(target=self._start_loop, args=(loop,), daemon=True)
            t.start()
            self.event_loops.append(loop)
            self.threads.append(t)

    def _start_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Set the given event loop in the current thread and run it forever."""
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def get_event_loop(self) -> Tuple[asyncio.AbstractEventLoop, int]:
        """
        Select an event loop from the pool based on current load (i.e., pending tasks).
        
        Returns:
            A tuple (selected_event_loop, index) where selected_event_loop is the least loaded
            asyncio.AbstractEventLoop and index is its index in the pool.
        """
        with self._lock:
            # Choose the loop with the fewest pending tasks.
            index = min(range(self.num_loops), key=lambda i: self.pending_tasks[i])
            self.pending_tasks[index] += 1 
            return self.event_loops[index], index

    def _decrement_pending(self, index: int) -> None:
        """Decrement the pending task counter for the event loop at the given index."""
        with self._lock:
            self.pending_tasks[index] -= 1
            
    def submit(self, async_func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Future:
        loop, index = self.get_event_loop()
        coro = async_func(*args, **kwargs)
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        # Decrement the counter when the task completes.
        future.add_done_callback(lambda f: self._decrement_pending(index))
        return future

    def run(self, async_func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        """
        Submit an asynchronous function to the least-loaded event loop and block until completion.
        
        Args:
            async_func: The asynchronous function to execute.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.
        
        Returns:
            A concurrent.futures.Future representing the task.
        """
        future = self.submit(async_func, *args, **kwargs)
        # Wait for the result and return it.
        return future.result()

    
    async def async_run(self, async_func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        """Submit an asynchronous function to the least-loaded event loop and return its result."""
        future = self.submit(async_func, *args, **kwargs)
        # Convert the concurrent.futures.Future into an awaitable asyncio.Future.
        async_future = asyncio.wrap_future(future, loop=asyncio.get_running_loop())
        return await async_future
                
    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown all event loops and join their threads.
        
        Args:
            wait: If True, block until all threads are terminated.
        """
        for loop in self.event_loops:
            loop.call_soon_threadsafe(loop.stop)
        for t in self.threads:
            t.join()
        self.event_loops.clear()
        self.threads.clear()
        self.pending_tasks.clear()
                
class AsyncManager:
    """
    A static manager for asynchronous execution in a synchronous context.
    
    By default, it uses MainThreadExecutor. To enable multithreading,
    call enable_multithreading() to switch to multithreaded event loops.
    """
    _executor: IAsyncExecutor = DefaultThreadExecutor()

    @staticmethod
    def run(async_func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        """
        Run the given asynchronous function using the underlying executor.
        """
        return AsyncManager._executor.run(async_func, *args, **kwargs)
    
    @staticmethod
    async def async_run_multiple(tasks: List[Callable[..., Awaitable[Any]]], max_workers=10, *args, **kwargs) -> AsyncGenerator[Any, None]:
        """
        Run multiple asynchronous functions in parallel using the underlying executor.
        Limits the number of concurrent tasks to max_workers.
        """
        import asyncio
        # Create a semaphore to limit concurrent tasks.
        semaphore = asyncio.Semaphore(max_workers)

        async def sem_task(task: Callable[..., Awaitable[Any]]) -> Any:
            async with semaphore:
                return await AsyncManager._executor.async_run(task, *args, **kwargs)
                
        coros = [sem_task(task) for task in tasks]
        for completed in asyncio.as_completed(coros):
            yield await completed

    @staticmethod
    def run_multiple(tasks: List[Callable[..., Awaitable[Any]]], max_workers=10, *args, **kwargs) -> Generator[Any, None, None]:
        """
        Run multiple asynchronous functions in parallel using the underlying executor. 
        Block calling thread and yield results as they complete.
        
        Args:
            tasks: A list of asynchronous functions to run.
            max_workers: The maximum number of concurrent tasks.
            *args: Positional arguments for the functions.
            **kwargs: Keyword arguments for the functions.
        """
        DONE = object()  # Sentinel value to indicate completion
        # Create a queue to hold results.
        result_queue: Queue = Queue()

        async def producer() -> None:
            async for result in AsyncManager.async_run_multiple(tasks, max_workers=max_workers, *args, **kwargs):
                # Put each result into the queue.
                result_queue.put(result)
            # Signal that all tasks are complete.
            result_queue.put(DONE)
            
        # Start the producer coroutine
        AsyncManager._executor.run(producer)

        # Yield results until all tasks are complete.
        POLL_INTERVAL = 0.01  # seconds
        done = False
        while not done:
            # Sleep briefly to avoid busy waiting.
            time.sleep(POLL_INTERVAL)
            while not result_queue.empty():
                result = result_queue.get()
                # Check for the sentinel value indicating completion.
                if result is DONE:
                    done = True
                    assert result_queue.empty(), "Queue should be empty after DONE is received."
                    break
                yield result  

                      
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
        AsyncManager._executor = EventLoopPoolExecutor(max_workers)
    
    @staticmethod
    def disable_multithreading() -> None:
        """
        Switch back to the main thread executor.
        """
        # Shut down the current executor if it's a BackgroundLoopExecutor
        AsyncManager._executor.shutdown(wait=True)
        # Create a new MainThreadExecutor
        AsyncManager._executor = DefaultThreadExecutor()