import asyncio
import pytest
from scraipe.extras.async_util import AsyncManager

async def async_add(a, b):
    await asyncio.sleep(0.01)
    return a + b

async def async_fail():
    await asyncio.sleep(0.01)
    raise RuntimeError("failure")

def test_run_success_main_thread():
    # Ensure main thread executor.
    AsyncManager.disable_multithreading()
    result = AsyncManager.run(async_add, 3, 4)
    assert result == 7

def test_run_exception_main_thread():
    AsyncManager.disable_multithreading()
    with pytest.raises(RuntimeError, match="failure"):
        AsyncManager.run(async_fail)

def test_run_success_multithreading():
    # Switch to multithreaded executor.
    AsyncManager.enable_multithreading(max_workers=2)
    result = AsyncManager.run(async_add, 10, 5)
    assert result == 15
    AsyncManager.disable_multithreading()

def test_run_exception_multithreading():
    AsyncManager.enable_multithreading(max_workers=2)
    with pytest.raises(RuntimeError, match="failure"):
        AsyncManager.run(async_fail)
    AsyncManager.disable_multithreading()