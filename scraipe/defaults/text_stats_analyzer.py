"""Module for analyzing text statistics."""

from scraipe.classes import IAnalyzer, AnalysisResult
from typing import Type
import re

class TextStatsAnalyzer(IAnalyzer):
    """Analyzer that computes word count, character count, sentence count, and average word length."""
    
    def analyze(self, content: str) -> AnalysisResult:
        """
        Analyze the provided text and return its statistics.

        Args:
            content (str): The text to be analyzed.

        Returns:
            AnalysisResult: An object containing an output dictionary with the following keys:
                - word_count (int): Total number of words.
                - character_count (int): Total number of characters.
                - sentence_count (int): Total number of sentences.
                - average_word_length (float): Average length of words in characters.
        """
        # Use a regex pattern that allows apostrophes in words
        words = re.findall(r"\b[\w']+\b", content)
        word_count = len(words)
        
        # Count total characters (including whitespace and punctuation)
        character_count = len(content)
        
        # Split content into sentences using punctuation as delimiters
        sentences = re.split(r'[.!?]+', content)
        # Filter out any empty strings resulting from the split
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)
        
        # Calculate average word length (avoid division by zero)
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        
        # Prepare the output dictionary
        stats = {
            "word_count": word_count,
            "character_count": character_count,
            "sentence_count": sentence_count,
            "average_word_length": avg_word_length,
        }
        
        return AnalysisResult.succeed(stats)