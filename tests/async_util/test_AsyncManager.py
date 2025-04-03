import asyncio
import pytest
from scraipe.extras.async_util import AsyncManager
from asdftimer import Timer
async def async_add(a, b):
    await asyncio.sleep(0.1)
    return a + b

async def async_fail():
    await asyncio.sleep(0.1)
    raise RuntimeError("failure")

async def async_double(x, sleep_time=.1):
    await asyncio.sleep(sleep_time)
    return x * 2

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

def test_run_multiple_success_main_thread():
    AsyncManager.disable_multithreading()
    tasks = [
        lambda: async_double(2,.5),
        lambda: async_double(3,.5),
        lambda: async_double(5,.5),
        lambda: async_double(10,.5),
    ]
    n = 50
    tasks *= n
    t = Timer()
    results = list(AsyncManager.run_multiple(tasks))
    elapsed = t.end()
    assert sorted(results) == sorted([4, 6, 10, 20] * n)
    assert elapsed < .6, f"Elapsed time {elapsed} exceeded expected threshold"
    AsyncManager.disable_multithreading()

def test_run_multiple_success_multithreading():
    AsyncManager.enable_multithreading(max_workers=10)
    
    tasks = [
        lambda: async_double(2,.5),
        lambda: async_double(3,.5),
        lambda: async_double(5,.5),
    ]
    n=100
    tasks *= n
    t = Timer()
    results = list(AsyncManager.run_multiple(tasks))
    elapsed = t.end()
    assert sorted(results) == sorted([4, 6, 10] * n)
    assert elapsed < .6, f"Elapsed time {elapsed} exceeded expected threshold"
    AsyncManager.disable_multithreading()