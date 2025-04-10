import asyncio
import threading

from concurrent.futures import Future as ConcurrentFuture
from inspect import isawaitable


def get_running_thread() -> threading.Thread|None:
    """
    Returns the current running thread.
    """
    return threading.current_thread()
def get_running_loop() -> asyncio.AbstractEventLoop|None:
    """
    Returns the current running event loop or None if there is no running loop.
    """
    return asyncio._get_running_loop()


from typing import Protocol, runtime_checkable, Any, Awaitable
from inspect import isawaitable

@runtime_checkable
class FutureLike(Protocol):
    def result(self) -> Any: ...
    def done() -> bool: ...
    
def get_awaitable(future: FutureLike) -> Awaitable:
    """
    Converts a Future-like object to an awaitable. Should be called from async context.
    """
    if isawaitable(future):
        return future
    if isinstance(future, ConcurrentFuture):
        return (asyncio.wrap_future(future))