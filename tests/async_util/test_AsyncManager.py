import asyncio
import pytest
from scraipe.async_util import AsyncManager
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

async def async_sleep(sleep_time=.1):
    await asyncio.sleep(sleep_time)
    return sleep_time

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
    AsyncManager.enable_multithreading(2)
    result = AsyncManager.run(async_add, 10, 5)
    assert result == 15
    AsyncManager.disable_multithreading()

def test_run_exception_multithreading():
    AsyncManager.enable_multithreading(2)
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
    results = list(AsyncManager.run_multiple(tasks,max_workers=1000))
    elapsed = t.end()
    assert sorted(results) == sorted([4, 6, 10, 20] * n)
    assert elapsed < .6, f"Elapsed time {elapsed} exceeded expected threshold"
    AsyncManager.disable_multithreading()

def test_run_multiple_success_multithreading():
    AsyncManager.enable_multithreading(pool_size=1)
    
    tasks = [
        lambda: async_double(2,.5),
        lambda: async_double(3,.5),
        lambda: async_double(5,.5),
    ]
    n=5
    tasks *= n
    t = Timer()
    results = list(AsyncManager.run_multiple(tasks,max_workers=10000))
    elapsed = t.end()
    assert sorted(results) == sorted([4, 6, 10] * n)
    assert elapsed < .6, f"Elapsed time {elapsed} exceeded expected threshold"
    AsyncManager.disable_multithreading()
    
def test_progressive_yields():
    # Test that AsyncManager.run_multiple yields results progressively as they are completed.
    AsyncManager.disable_multithreading()
    tasks = [
        lambda: async_sleep(0.2),
        lambda: async_sleep(.5),
        lambda: async_sleep(.75),
        lambda: async_sleep(1),
    ]
    
    # Measure the time for each task to complete
    t = Timer()
    generator = AsyncManager.run_multiple(tasks, max_workers=10) 
    results = []
    for result in generator:
        results.append(result)
        elapsed = t.end()
        print(f"Yielded result: {result}, elapsed time: {elapsed:.2f} seconds")
        assert pytest.approx(result, abs=.1) == elapsed

def test_progressive_yields_multithreaded():
    # Test that AsyncManager.run_multiple yields results progressively as they are completed.
    AsyncManager.enable_multithreading(pool_size=10)
    tasks = [
        lambda: async_sleep(0.2),
        lambda: async_sleep(.5),
        lambda: async_sleep(.75),
        lambda: async_sleep(1),
    ]
    
    # Measure the time for each task to complete
    t = Timer()
    generator = AsyncManager.run_multiple(tasks, max_workers=10) 
    results = []
    for result in generator:
        results.append(result)
        elapsed = t.end()
        print(f"Yielded result: {result}, elapsed time: {elapsed:.2f} seconds")
        assert pytest.approx(result, abs=.1) == elapsed
