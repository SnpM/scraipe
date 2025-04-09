from scraipe.async_classes import IAsyncAnalyzer
from scraipe.classes import IAnalyzer, AnalysisResult
from scraipe.async_util import AsyncManager
from asyncio import Future
from typing import List, Tuple
import asyncio

class MultiAnalyzer(IAsyncAnalyzer):
    """
    MultiAnalyzer is a class that allows for the parallel execution of multiple analyzers.
    It can take IAnalyzer and IAsyncAnalyzer instances and can be used to run multiple
    analyzers concurrently.
    """

    def __init__(self, analyzers: list[IAnalyzer], max_workers: int=10, debug: bool=False, debug_delimiter:str = "; "):
        assert len(analyzers) > 0, "No analyzers provided."
        assert all(isinstance(analyzer, (IAnalyzer)) for analyzer in analyzers), \
            "All analyzers must extend IAnalyzer."
        assert isinstance(max_workers, int) and max_workers > 0, "max_workers must be a positive integer."
            
        self.max_workers = max_workers
        self.debug = debug
        self.debug_delimiter = debug_delimiter
        self.analyzers = analyzers

        # Split analyzers into async and sync and store ids
        self.sync_analyzers: List[Tuple[int, IAnalyzer]] = []
        self.async_analyzers: List[Tuple[int, IAnalyzer]] = []
        for id_analyzer in enumerate(analyzers):
            if isinstance(id_analyzer[1], IAsyncAnalyzer):
                self.async_analyzers.append(id_analyzer)
            else:
                self.sync_analyzers.append(id_analyzer)
                
    async def run_async_analyze(self, id: int, analyzer: IAsyncAnalyzer, content) -> Tuple[int, AnalysisResult]:
        return id, await analyzer.async_analyze(content)    
    
    async def _submit_async_analyzers(self, content) -> List[Future]:
        # Submit all async analyzer tasks for parallel execution

        tasks = [self.run_async_analyze(id, analyzer, content) for id, analyzer in self.async_analyzers]
        
        futures = []
        # Submit tasks to the executor
        for task in tasks:
            future = AsyncManager.get_executor().submit(task)
            futures.append(future)        
        return futures
        
    def _run_sync_analyzers(self, content) -> List[Tuple[int, AnalysisResult]]:
        # Run all sync analyzers in serial
        results_with_ids: List[Tuple[int, AnalysisResult]] = []
        for id, analyzer in self.sync_analyzers:
            result = analyzer.analyze(content)
            results_with_ids.append((id, result))
        return results_with_ids
    
    def _process_results_with_ids(self, results_with_ids: List[Tuple[int, AnalysisResult]]) -> AnalysisResult:
        # Create an output dict and populate it with results' outputs
        # If there is a conflict, prefix the key with the analyzer's class name+id; e.g. TextScraper-0_dataname
        
        # Create debug log
        success = False
        debug_chain = [None] * len(self.analyzers)
        for id, result in results_with_ids:
            if result.analysis_success:
                debug_chain[id] = (f"{self.analyzers[id].__class__}[SUCCESS]")
                success = True
            else:
                debug_chain[id] = (f"{self.analyzers[id].__class__}[FAIL]: {result.analysis_error}")
        assert all(debug_chain), "All analyzers must return a result."
        
        if success:
            # find conflicting keys
            keys = set()
            conflicting_keys = set()
            for id, result in results_with_ids:
                if result.output is not None:
                    for key in result.output.keys():
                        if key in keys:
                            conflicting_keys.add(key)
                        else:
                            keys.add(key)
            
            # Create output dict
            output = {}
            for id, result in results_with_ids:
                if result.output is not None:
                    for key, value in result.output.items():
                        if key in conflicting_keys:
                            class_name = self.analyzers[id].__class__.__name__
                            output[f"{class_name}-{id}_{key}"] = value
                        else:
                            output[key] = value
            
            success_result = AnalysisResult.succeed(output)
            if self.debug:
                success_result.analysis_error = self.debug_delimiter.join(debug_chain)
            return success_result
        else:
            # If all analyzers failed, return a fail result
            debug_message = "All analyzers failed... " + self.debug_delimiter.join(debug_chain)
            return AnalysisResult.fail(debug_message)

    async def async_analyze(self, content):
        futures = await self._submit_async_analyzers(content)
        # Run sync analyzers in serial
        sync_results_with_ids = self._run_sync_analyzers(content)
        # Wrap futures
        futures = [asyncio.wrap_future(future) for future in futures]
        # Wait for all async results
        async_results_with_ids = [await completed for completed in asyncio.as_completed(futures)]
        # Combine sync and async results
        results_with_ids = sync_results_with_ids + async_results_with_ids
        # Process results with ids using instance method
        return self._process_results_with_ids(results_with_ids)

