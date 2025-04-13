import pytest
import asyncio
from scraipe.async_util.async_executors import IAsyncExecutor, EventLoopPoolExecutor, DefaultBackgroundExecutor
from asdftimer import AsdfTimer as Timer

@pytest.fixture(params=[EventLoopPoolExecutor, DefaultBackgroundExecutor])
def executor(request):
    executor_instance = request.param()
    yield executor_instance
    executor_instance.shutdown(wait=True)

async def successful_async_function(a, b):
    await asyncio.sleep(0.01)
    return a + b

async def failing_async_function():
    await asyncio.sleep(0.01)
    raise ValueError('Test exception')

@pytest.mark.asyncio
async def test_common_executor_harness(executor:IAsyncExecutor):
    async def sample_task():
        await asyncio.sleep(0.01)
        return "OK"
    result = await executor.async_run(sample_task())
    assert result == "OK"

def test_success(executor):
    result = executor.run(successful_async_function(5, 7))
    assert result == 12

def test_exception(executor):
    with pytest.raises(ValueError, match='Test exception'):
        executor.run(failing_async_function())

def test_parallel_runs(executor):
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
async def test_async_run_success(executor):
    result = await executor.async_run(successful_async_function(5, 7))
    assert result == 12

@pytest.mark.asyncio
async def test_async_run_exception(executor):
    with pytest.raises(ValueError, match='Test exception'):
        await executor.async_run(failing_async_function())

@pytest.mark.asyncio
async def test_async_run_parallel(executor):
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

def test_run_multiple(executor):
    async def async_task(x):
        await asyncio.sleep(0.1)
        return x * 2

    tasks = [async_task(i) for i in range(5)]
    results = [result for result,err in executor.run_multiple(tasks)]
    assert sorted(results) == sorted([i * 2 for i in range(5)])

@pytest.mark.asyncio
async def test_async_run_multiple(executor:IAsyncExecutor):
    async def async_task(x):
        await asyncio.sleep(0.1)
        return x * 2
    n = 10
    tasks = [async_task(i) for i in range(n)]
    results = [result async for result,err in executor.run_multiple_async(tasks)]
    assert sorted(results) == sorted([i * 2 for i in range(n)])

@pytest.mark.asyncio
async def test_run_from_event_loop(executor):
    loop = asyncio.get_event_loop()
    
    async def func1():
        await asyncio.sleep(0.1)
        print("func1 done")
        return "func1 " + await func2()
    async def func2():
        await asyncio.sleep(0.1)
        print("func2 done")
        return "func2"
    
    result = executor.run(func1())
    assert "func1" in result
    assert "func2" in result