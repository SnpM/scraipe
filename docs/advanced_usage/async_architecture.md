# Async Architecture


Many scraping and analysis tasks are IO-bound meaning we have to wait a lot for network responses. To achieve high performance, most scrapers and analyzers need to execute their logic asynchronously. Scraipe's synchronous API cannot directly execute asynchronous code, so Scraipe manages this interaction under the hood.

 This page provides a deep dive into how Scraipe seamlessly orchestrates synchronous and asynchronous code. If you just want to create async components, check out the guide on [custom components](./custom_components.md#async-scrapers-and-analyzers).

## Async Interfaces

Scraipe provides two primary interfaces for asynchronous operations: [`IAsyncScraper`][scraipe.async_classes.IAsyncScraper] and [`IAsyncAnalyzer`][scraipe.async_classes.IAsyncAnalyzer]. These interfaces extend their synchronous counterparts ([`IScraper`][scraipe.classes.IScraper] and [`IAnalyzer`][scraipe.classes.IAnalyzer]).

- **IAsyncScraper**: Designed for asynchronous scraping. It allows you to implement `async_scrape()` for non-blocking operations and provides synchronous wrappers (`scrape()`, `scrape_multiple`) for compatibility with synchronous workflows.
- **IAsyncAnalyzer**: Designed for asynchronous analysis tasks. Similar to `IAsyncScraper`, it provides `async_analyze()` for non-blocking analysis and provides synchronous wrappers (`analyze()`, `scrape_multiple`).

The synchronous wrappers use Async Orchestration to run the async functions from a synchronous context. As soon as you implement `IAsyncScraper.async_scrape()`, the class will behave like a normal `IScraper` without any additional configuration.

## Async Orchestration

Scraipe's async orchestration is powered by the [`AsyncManager`][scraipe.async_util.async_manager.AsyncManager] and implementations of `IAsyncExecutor`. These components ensure seamless integration of asynchronous operations within a synchronous API.

### [IAsyncExecutor][scraipe.async_util.async_executors.IAsyncExecutor]

Executors manage the execution of asynchronous tasks. Scraipe provides two implementations of `IAsyncExecutor`:
- [`DefaultBackgroundExecutor`][scraipe.async_util.async_executors.DefaultBackgroundExecutor]: Runs a single asyncio event loop in a dedicated background thread. This is the default executor used by `AsyncManager`.
- [`EventLoopPoolExecutor`][scraipe.async_util.async_executors.EventLoopPoolExecutor]: Manages a pool of asyncio event loops, each running in its own thread. It balances tasks across the pool for improved concurrency.

### [`AsyncManager`][scraipe.async_util.AsyncManager]

The `AsyncManager` is a static provider for an `IAsyncExecutor` instance.

- `get_executor()`: Get the singleton executor instance. This is a `DefaultBackgroundExecutor` instance by default.
- `set_executor()`: Allows switching between the singleton executor instances.
- `enable_multithreading(pool_size: int = 3)`: Enables multithreading by switching the executor to an instance of `EventLoopPoolExecutor`. It creates a pool of the given size.
- `disable_multithreading()`: Disables multithreading by switching the executor to an instance of `DefaultBackgroundExecutor`.