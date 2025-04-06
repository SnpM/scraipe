# Async Architecture

Scraipe features a highly portable synchronous API. Unfortunately, many scraping and analysis tasks are IO-bound meaning we have to wait a lot for network responses. To achieve high performance, most scrapers and analyzers need to execute their logic in asynchronously. This page provides a deep dive into how Scraipe seamlessly orchestrates synchronous and asynchronous code. If you just want to create async components, check out the guide on [custom components](./custom_components.md#async-scrapers-and-analyzers).

## Async Interfaces

Scraipe provides two primary interfaces for asynchronous operations: [`IAsyncScraper`][scraipe.async_classes.IAsyncScraper] and [`IAsyncAnalyzer`][scraipe.async_classes.IAsyncAnalyzer]. These interfaces extend their synchronous counterparts ([`IScraper`][scraipe.classes.IScraper] and [`IAnalyzer`][scraipe.classes.IAnalyzer]).

- **IAsyncScraper**: Designed for asynchronous scraping. It allows you to implement `async_scrape()` for non-blocking operations and provides synchronous wrappers (`scrape()`, `scrape_multiple`) for compatibility with synchronous workflows.
- **IAsyncAnalyzer**: Designed for asynchronous analysis tasks. Similar to `IAsyncScraper`, it provides `async_analyze()` for non-blocking analysis and provides synchronous wrappers (`analyze()`, `scrape_multiple`).

The synchronous wrappers use Async Orchestration to run the async functions from a synchronous context. As soon as you implement `IAsyncScraper.async_scrape()`, the class will behave like a normal `IScraper` without any additional configuration.

## Async Orchestration

Scraipe's async orchestration is powered by the [`AsyncManager`][scraipe.async_util.AsyncManager] and implementations of `IAsyncExecutor`. These components ensure seamless integration of asynchronous operations within a synchronous API.

### [IAsyncExecutor][scraipe.async_util.IAsyncExecutor]

Executors manage the execution of asynchronous tasks. Scraipe provides two implementations of `IAsyncExecutor`:
- [`DefaultBackgroundExecutor`][scraipe.async_util.DefaultBackgroundExecutor]: Runs a single asyncio event loop in a dedicated background thread. This is the default executor used by `AsyncManager`.
- [`EventLoopPoolExecutor`][scraipe.async_util.EventLoopPoolExecutor]: Manages a pool of asyncio event loops, each running in its own thread. It balances tasks across the pool for improved concurrency.

### [`AsyncManager`][scraipe.async_util.AsyncManager]

The `AsyncManager` is a static utility that abstracts the complexity of running asynchronous tasks. It's essentially a static wrapper for an instance of an executor.

It provides the following functions for async integration.
- `run()`: Executes a coroutine and blocks until it completes.
- `run_multiple()`: Executes multiple coroutines concurrently and yields results as they complete.

Additionally, class's executor can be configured:
- `set_executor()`: Allows switching between executor instances.
- `enable_multithreading()`: Enables multithreading by switching the executor to an instance of `EventLoopPoolExecutor`.
- `disable_multithreading()`: Disables multithreading by switching the executor to an instance of `DefaultBackgroundExecutor`.