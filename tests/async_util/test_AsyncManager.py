import asyncio
import pytest
from scraipe.async_util import AsyncManager
from asdftimer import AsdfTimer as Timer
from tests.async_util.utils import generate_tasks

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
    result = AsyncManager.run(async_add(3, 4))
    assert result == 7

def test_run_exception_main_thread():
    AsyncManager.disable_multithreading()
    with pytest.raises(RuntimeError, match="failure"):
        AsyncManager.run(async_fail())

def test_run_success_multithreading():
    # Switch to multithreaded executor.
    AsyncManager.enable_multithreading(2)
    result = AsyncManager.run(async_add(10, 5))
    assert result == 15
    AsyncManager.disable_multithreading()

def test_run_exception_multithreading():
    AsyncManager.enable_multithreading(2)
    with pytest.raises(RuntimeError, match="failure"):
        AsyncManager.run(async_fail())
    AsyncManager.disable_multithreading()

def test_run_multiple_success():
    AsyncManager.disable_multithreading()
    tasks = lambda:[
        async_double(2, .5),
        async_double(3, .5),
        async_double(5, .5),
        async_double(10, .5),
    ]
    n = 1
    tasks = generate_tasks(tasks, n)
    
    # Wait for previous tasks to finish
    AsyncManager.run(asyncio.sleep(0.01))
    
    t = Timer()
    results = list(AsyncManager.run_multiple(tasks, max_workers=1000))
    t.stop()
    assert sorted(results) == sorted([4, 6, 10, 20] * n)
    assert t.elapsed < .6, f"Elapsed time {t.elapsed} exceeded expected threshold"
    AsyncManager.disable_multithreading()

def test_run_multiple_success_multithreaded():
    AsyncManager.enable_multithreading(pool_size=2)
    
    tasks = lambda:[
        async_double(2, .5),
        async_double(3, .5),
        async_double(5, .5),
    ]
    n = 5
    tasks = generate_tasks(tasks, n)
    
    # Wait for previous tasfks to finish
    AsyncManager.run(asyncio.sleep(0.01))
    
    t = Timer()
    results = list(AsyncManager.run_multiple(tasks, max_workers=10000))
    elapsed = t.stop()
    assert sorted(results) == sorted([4, 6, 10] * n)
    assert elapsed < .6, f"Elapsed time {elapsed} exceeded expected threshold"
    AsyncManager.disable_multithreading()
    
def test_progressive_yields():
    # Test that AsyncManager.run_multiple yields results progressively as they are completed.
    AsyncManager.disable_multithreading()
    tasks = [
        async_sleep(0.2),
        async_sleep(0.5),
        async_sleep(0.75),
        async_sleep(1),
    ]
    
    # Measure the time for each task to complete
    t = Timer()
    generator = AsyncManager.run_multiple(tasks, max_workers=10) 
    results = []
    for result in generator:
        results.append(result)
        elapsed = t.elapsed
        print(f"Yielded result: {result}, elapsed time: {elapsed:.2f} seconds")
        assert pytest.approx(result, abs=0.1) == elapsed

def test_progressive_yields_multithreaded():
    # Test that AsyncManager.run_multiple yields results progressively as they are completed.
    AsyncManager.enable_multithreading(pool_size=10)
    # Wait for previous tasks to finish
    AsyncManager.run(asyncio.sleep(0.01))
    
    tasks = lambda:[
        async_sleep(0.2),
        async_sleep(0.5),
        async_sleep(0.75),
        async_sleep(1),
    ]
    tasks = tasks()
    
    t = Timer()
    generator = AsyncManager.run_multiple(tasks, max_workers=10) 
    results = []
    for result in generator:
        results.append(result)
        elapsed = t.elapsed
        print(f"Yielded result: {result}, elapsed time: {elapsed:.2f} seconds")
        assert pytest.approx(result, abs=0.1) == elapsed
