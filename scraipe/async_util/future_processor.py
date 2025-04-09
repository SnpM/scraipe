
import threading
from queue import Queue
from concurrent.futures import Future
from typing import Any, Tuple, final, Set, List
import time
from concurrent.futures import ThreadPoolExecutor

from scraipe.async_util.common import get_running_loop
@final
class AtomicCounter:
    def __init__(self, start=0):
        self.value = start
        self.lock = threading.Lock()

    def pop(self):
        with self.lock:
            self.value += 1
            return self.value
@final
class ResultHolder:
    def __init__(self,  success: bool, output: Any = None, exception: Exception = None):
        self.success = success
        self.output = output
        self.exception = exception
    def __repr__(self):
        return f"ResultHolder(success={self.success}, output={self.output}, exception={self.exception})"
        
@final
class FutureProcessor:
    """
    A class that uses a dedicated thread to process results from concurrent Futures.

    Usage:
        processor = FutureResultProcessor()
        result = processor.process_future_result(future)
    """    
    POLL_INTERVAL = 0.01
    
    done_futures:Queue[Tuple[int, Future]]
    done_results:dict[ResultHolder]
    locks:List[threading.Lock]
    NUM_LOCKS = 16 # Number of concurrent threads that can access the done_results dictionary
    
    def __init__(self) -> None:
        self.done_futures = Queue()
        self.done_results = dict()
        self.atomic_counter = AtomicCounter()
        self._thread = threading.Thread(target=self._dispatcher, daemon=True)
        self._thread.start()
        
        # assert self.NUM_LOCKS is a power of 2
        assert (self.NUM_LOCKS & (self.NUM_LOCKS - 1)) == 0, "NUM_LOCKS must be a power of 2"
        self.locks = [threading.Lock() for _ in range(self.NUM_LOCKS)]
        
        
    def _dispatcher(self):
        while True:               
            # Get results from done futures
            id, future = self.done_futures.get()
            assert future.done(), "Future is not done"
            result_holder = None
            if future.cancelled():
                result_holder = ResultHolder(success=False, exception=RuntimeError("Future was cancelled"))
            else:
                try:
                    result = future.result()
                    result_holder = ResultHolder(success=True, output=result)
                except Exception as e:
                    result_holder = ResultHolder(success=False, exception=e)
            self.done_results[id] = result_holder     
                
    def on_done(self, id, future: Future) -> None:
        """
        Callback to be called when the Future is done.
        """
        self.done_futures.put((id, future))

    def get_future_result(self, future: Future,) -> Any:
        """
        Blocks until the result of the given Future is ready, even if called from an event loop thread.

        Args:
            future: A concurrent.futures.Future object.

        Returns:
            The result of the future, or raises its exception.
        """
        # if threading.current_thread() is self._thread:
        #     raise RuntimeError("Cannot call process_future_result from within the result processor thread")
        
        id = self.atomic_counter.pop()
        future.add_done_callback(lambda f: self.on_done(id, future))
                
        # Check if we are in an event loop
        loop = get_running_loop()
        if loop is None:
            # Block until the result is ready
            while id not in self.done_results:
                time.sleep(self.POLL_INTERVAL)
        else:
            raise RuntimeError("Cannot call process_future_result from within an event loop")
        
        # Get the result from done pile
        # Should be thread-safe because dict.pop() on unique key is atomic in theory
        result_holder = self.done_results.pop(id, None)
        if result_holder is None:
            raise RuntimeError("Future not found in done pile")
        
        # Return the result or raise the exception
        if result_holder.success:
            return result_holder.output
        else:
            raise result_holder.exception