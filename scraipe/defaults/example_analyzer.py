from scraipe.classes import IAnalyzer, AnalysisResult
class ExampleAnalyzer(IAnalyzer):
    """A minimal analyzer implementation for example."""
    def analyze(self, content: str) -> AnalysisResult:
        # Fail if content is malicious!
        if "hacker" in content:
            return AnalysisResult.fail("Hacker detected!")
        # Simulate a successful analysis; reverses the content
        result = content[::-1]
        output = {"reversed_content": result}
        return AnalysisResult.success(output)