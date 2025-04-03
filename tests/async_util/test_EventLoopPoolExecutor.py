import asyncio
import pytest
from scraipe.async_util import EventLoopPoolExecutor
from asdftimer import Timer

async def successful_async_function(a, b):
    await asyncio.sleep(0.01)
    return a + b

async def failing_async_function():
    await asyncio.sleep(0.01)
    raise ValueError('Test exception')

def test_success():
    executor = EventLoopPoolExecutor()
    result = executor.run(successful_async_function, 5, 7)
    assert result == 12
    executor.shutdown(wait=True)

def test_exception():
    executor = EventLoopPoolExecutor()
    with pytest.raises(ValueError, match='Test exception'):
        executor.run(failing_async_function)
    executor.shutdown(wait=True)

def test_parallel_runs():
    executor = EventLoopPoolExecutor()
    
    async def async_task():
        await asyncio.sleep(1)
        return "done"
    async def run_tasks():
        tasks = [async_task() for _ in range(10)]
        return await asyncio.gather(*tasks)
    
    t = Timer(disable_print=True)
    result = executor.run(run_tasks)
    duration = t.end()
    executor.shutdown(wait=True)
    assert result == ["done"] * 10
    assert duration < 1.1, f"Expected duration < 1.1 seconds, got {duration:.2f} seconds"

@pytest.mark.asyncio
async def test_async_run_success():
    executor = EventLoopPoolExecutor()
    result = await executor.async_run(successful_async_function, 5, 7)
    assert result == 12
    executor.shutdown(wait=True)

@pytest.mark.asyncio
async def test_async_run_exception():
    executor = EventLoopPoolExecutor()
    with pytest.raises(ValueError, match='Test exception'):
        await executor.async_run(failing_async_function)
    executor.shutdown(wait=True)

@pytest.mark.asyncio
async def test_async_run_parallel_runs():
    executor = EventLoopPoolExecutor()
    async def async_task():
        await asyncio.sleep(1)
        return "done"
    async def run_tasks():
        tasks = [async_task() for _ in range(10)]
        return await asyncio.gather(*tasks)
    t = Timer(disable_print=True)
    result = await executor.async_run(run_tasks)
    duration = t.end()
    executor.shutdown(wait=True)
    assert result == ["done"] * 10
    assert duration < 1.1, f"Expected duration < 1.1 seconds, got {duration:.2f} seconds"