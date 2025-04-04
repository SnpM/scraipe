import asyncio
import pytest
from scraipe.async_util import DefaultBackgroundExecutor
from asdftimer import AsdfTimer as Timer

async def successful_async_function(a, b):
    await asyncio.sleep(0.01)
    return a + b

async def failing_async_function():
    await asyncio.sleep(0.01)
    raise ValueError('Test exception')

def test_success():
    executor = DefaultBackgroundExecutor()
    result = executor.run(successful_async_function(5, 7))
    assert result == 12

def test_exception():
    executor = DefaultBackgroundExecutor()
    with pytest.raises(ValueError, match='Test exception'):
        executor.run(failing_async_function())

def test_parallel_runs():
    executor = DefaultBackgroundExecutor()
    
    async def async_task():
        await asyncio.sleep(1)
        return "done"
    
    n = 5
    async def run_tasks():
        tasks = [async_task() for _ in range(n)]
        return await asyncio.gather(*tasks)
    
    # Wait for previous tasks to finish
    executor.run(asyncio.sleep(0.01))
    
    with Timer() as t:
        # Run tasks in parallel
        result = executor.run(run_tasks())
        elapsed = t.elapsed
    
    assert result == ["done"] * n
    assert elapsed < 1.2, f"Expected duration < 1.1 seconds, got {elapsed:.2f} seconds"

@pytest.mark.asyncio
async def test_async_run_success():
    executor = DefaultBackgroundExecutor()
    result = await executor.async_run(successful_async_function(5, 7))
    assert result == 12

@pytest.mark.asyncio
async def test_async_run_exception():
    executor = DefaultBackgroundExecutor()
    with pytest.raises(ValueError, match='Test exception'):
        await executor.async_run(failing_async_function())

@pytest.mark.asyncio
async def test_async_run_parallel():
    executor = DefaultBackgroundExecutor()
    async def async_task():
        await asyncio.sleep(1)
        return "done"
    
    n = 5
    async def run_tasks():
        tasks = [async_task() for _ in range(n)]
        return await asyncio.gather(*tasks)
    
    # Wait for previous tasks to finish
    executor.run(asyncio.sleep(0.01))
    
    t = Timer(disable_print=True)
    result = await executor.async_run(run_tasks())
    duration = t.stop()
    assert result == ["done"] * n
    assert duration < 1.1, f"Expected duration < 1.1 seconds, got {duration:.2f} seconds"