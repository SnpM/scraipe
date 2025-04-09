import asyncio
import threading
from concurrent.futures import Future

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

def wrap_asyncio_future(async_future: asyncio.Future) -> Future:
    blocking_future = Future()

    def transfer_result(asyncio_future: asyncio.Future):
        try:
            result = asyncio_future.result()  # Grab result or raise exception
            blocking_future.set_result(result)
        except Exception as e:
            blocking_future.set_exception(e)

    async_future.add_done_callback(transfer_result)
    return blocking_future