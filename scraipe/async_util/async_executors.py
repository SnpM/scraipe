from abc import abstractmethod, ABC
import asyncio
from typing import final, Any, Callable, Awaitable, List, Generator, Tuple, AsyncGenerator
import threading
from queue import Queue
import time
import asyncio
from scraipe.async_util.common import get_running_loop, get_running_thread
from scraipe.async_util.common import FutureLike, get_awaitable

import logging


@final
class TaskInfo:
    def __init__(self, future:FutureLike, event_loop:asyncio.AbstractEventLoop=None, thread:threading.Thread=None):
        """
        Stores information about a task for managing its execution in different contexts.
        """
        self.future = future
        self.event_loop = event_loop
        self.thread = thread
class TaskResult:
    def __init__(self, success:bool, output:Any=None, exception:Exception=None):
        """
        Represents the result of a task execution.
        """
        self.success = success
        self.output = output
        self.exception = exception

# Base interface for asynchronous executors.
class IAsyncExecutor:
    @abstractmethod
    def submit(self, coro: Awaitable[Any]) -> FutureLike:
        """
        Submit a coroutine to the executor.

        Args:
            coro: The coroutine to execute.

        Returns:
            A Future object representing the execution of the coroutine.
        """
        raise NotImplementedError("Must be implemented by subclasses.")
    
    def run(self, coro: Awaitable[Any]) -> Any:
        """
        Run a coroutine in the executor and block until it completes.
        
        Args:
            coro: The coroutine to execute.
        
        Returns:
            The result of the coroutine.
        """
        future = self.submit(coro)
        # Assert that future is FutureLike
        assert isinstance(future, FutureLike), f"Expected {FutureLike}, got {type(future)}"
        result = future.result()
        
        return result
    
    async def async_run(self, coro: Awaitable[Any]) -> Any:
        future = self.submit(coro)
        # Assert that future is FutureLike
        assert isinstance(future, FutureLike), f"Expected {FutureLike}, got {type(future)}"
        awaitable = get_awaitable(future)
        return await awaitable
    
    async def wait_for(self, future: FutureLike) -> Any:
        return await get_awaitable(future)
            
    async def run_multiple_async(self, tasks: List[Awaitable[Any]], max_workers:int=10) -> AsyncGenerator[Tuple[Any, str], None]:
        """
        Run multiple coroutines in parallel using the underlying executor.
        Limits the number of concurrent tasks to max_workers.
        
        Args:
            tasks: A list of coroutines to run.
            max_workers: The maximum number of concurrent tasks.
        Yields:
            A tuple of (result, error) for each task.
        """
        assert max_workers > 0, "max_workers must be greater than 0"
        semaphore = asyncio.Semaphore(max_workers)
        
        async def work(coro: Awaitable[Any], sem: asyncio.Semaphore) -> Tuple[Any, str]:
            async with sem:
                try:
                    return await self.async_run(coro),None
                except Exception as e:
                    logging.error(f"Task failed with exception: {e}")
                    return None, str(e)
                
        coros = [work(task, semaphore) for task in tasks]
        for completed in asyncio.as_completed(coros):
            yield await completed

    def run_multiple(self, tasks: List[Awaitable[Any]], max_workers:int=10) -> Generator[Tuple[Any,str], None, None]:
        """
        Run multiple coroutines in parallel using the underlying executor.
        Block calling thread and yield results as they complete.
        
        Args:
            tasks: A list of coroutines to run.
            max_workers: The maximum number of concurrent tasks.
            
        Yields:
            A tuple of (result, error) for each task.
        """
        DONE = object()  # Sentinel value to indicate completion
        result_queue: Queue = Queue()

        async def producer() -> None:
            async for result in self.run_multiple_async(tasks, max_workers=max_workers):
                result_queue.put(result)
            result_queue.put(DONE)
        
        self.submit(producer())
        
        POLL_INTERVAL = 0.01  # seconds
        done = False
        while not done:
            time.sleep(POLL_INTERVAL)
            while not result_queue.empty():
                result = result_queue.get()
                if result is DONE:
                    done = True
                    break
                yield result
    
    def shutdown(self, wait: bool = True) -> None:
        pass    

@final
class DefaultBackgroundExecutor(IAsyncExecutor):
    """Maintains a single dedicated thread for an asyncio event loop."""
    def __init__(self) -> None:
        def _start_loop() -> None:
            """Set the event loop in the current thread and run it forever."""
            asyncio.set_event_loop(self._loop)
            self._loop.run_forever()
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=_start_loop, daemon=True)
        self._thread.start()
        
        
    def submit(self, coro: Awaitable[Any]) -> FutureLike:
        """
        Submit a coroutine to the executor.
        
        Args:
            coro: The coroutine to execute.
        
        Returns:
            A Future object representing the execution of the coroutine.
        """
        #assert get_running_loop() is not self._loop, "Cannot submit to the same event loop"
        return asyncio.run_coroutine_threadsafe(coro, self._loop)
    
    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the executor and stop the event loop.
        
        Args:
            wait: If True, block until the thread is terminated.
        """
        self._loop.call_soon_threadsafe(self._loop.stop)
        if wait:
            # Check if the thread is the calling thread
            if threading.current_thread() is not self._thread:
                # Wait for the thread to finish
                self._thread.join()
            else:
                # If the calling thread is the same as the executor thread, we can't join it.
                # So we just stop the loop and let it exit.
                pass
        self._loop.close()

class EventLoopPoolExecutor(IAsyncExecutor):
    """
    A utility class that manages a pool of persistent asyncio event loops,
    each running in its own dedicated thread. It load balances tasks among
    the event loops by tracking pending tasks and selecting the loop with
    the smallest load.
    """
    def __init__(self, pool_size: int = 1) -> None:
        self.pool_size = pool_size
        self.event_loops: List[asyncio.AbstractEventLoop] = []
        self.threads: List[threading.Thread] = []
        # Track the number of pending tasks per event loop.
        self.pending_tasks: List[int] = [0] * pool_size
        self._lock = threading.Lock()

        for _ in range(pool_size):
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
            index = min(range(self.pool_size), key=lambda i: self.pending_tasks[i])
            self.pending_tasks[index] += 1 
            return self.event_loops[index], index

    def _decrement_pending(self, index: int) -> None:
        """Decrement the pending task counter for the event loop at the given index."""
        with self._lock:
            self.pending_tasks[index] -= 1
            
    def submit(self, coro: Awaitable[Any]) -> FutureLike:
        """
        Submit a coroutine to the executor.
        
        Args:
            coro: The coroutine to execute.
        
        Returns:
            A Future object representing the execution of the coroutine.
        """
        loop, index = self.get_event_loop()
        future = None
        if get_running_loop() is loop:
            # If the current thread is the same as the event loop's thread, run it directly.
            future = asyncio.ensure_future(coro, loop=loop)
        else:
            # Otherwise, run it in the event loop's thread.
            future = asyncio.run_coroutine_threadsafe(coro, loop)
            
        future.add_done_callback(lambda f: self._decrement_pending(index))
        return future
                
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