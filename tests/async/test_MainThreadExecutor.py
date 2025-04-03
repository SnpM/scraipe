import asyncio
import pytest
from scraipe.async_util import DefaultThreadExecutor

async def successful_async_function(a, b):
    await asyncio.sleep(0.01)
    return a + b

async def failing_async_function():
    await asyncio.sleep(0.01)
    raise ValueError('Test exception')

def test_main_thread_executor_success():
    executor = DefaultThreadExecutor()
    result = executor.run(successful_async_function, 5, 7)
    assert result == 12

def test_main_thread_executor_exception():
    executor = DefaultThreadExecutor()
    with pytest.raises(ValueError, match='Test exception'):
        executor.run(failing_async_function)
