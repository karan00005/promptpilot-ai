import unittest
import sys
import os

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.token_counter import count_tokens, estimate_cost
from services.compression.rule_based import compress_rule_based
from services.compression.heuristic import compress_heuristic
from services.compression.summarizer import fallback_summarize_paragraph

class TestPromptPilotEngine(unittest.TestCase):
    
    def test_token_counter(self):
        # Empty text
        self.assertEqual(count_tokens(""), 0)
        
        # Standard counting
        text = "Hello world! This is a token test."
        tokens = count_tokens(text, model="gpt-4o")
        self.assertGreater(tokens, 0)
        
        # Cost estimation
        cost = estimate_cost(100000, model="gpt-4o")
        # 100k tokens at $5.00/1M should be exactly $0.50
        self.assertAlmostEqual(cost, 0.50, places=4)
        
    def test_rule_based_compression(self):
        # Test stripping of polite words
        prompt = "Hello! Could you please help me write a python function? Thanks in advance!"
        compressed = compress_rule_based(prompt)
        
        # "Hello", "Could you", "please", "Thanks in advance" should be gone
        self.assertNotIn("please", compressed.lower())
        self.assertNotIn("hello", compressed.lower())
        self.assertNotIn("thanks", compressed.lower())
        self.assertIn("help me write a python function", compressed.lower())
        
        # Test verbose phrases replacement
        verbose_prompt = "I need this in order to deploy our system due to the fact that it is critical."
        compressed_verbose = compress_rule_based(verbose_prompt)
        
        self.assertNotIn("in order to", compressed_verbose)
        self.assertNotIn("due to the fact that", compressed_verbose)
        self.assertIn("to deploy our system", compressed_verbose)
        self.assertIn("because it is critical", compressed_verbose)
        
    def test_heuristic_compression(self):
        # Test preserving code blocks and critical instructions
        prompt_with_code = (
            "Here is the context of my project.\n\n"
            "```python\ndef calculate(a, b):\n    return a + b\n```\n\n"
            "You must optimize this code immediately for production. Always write clean variables."
        )
        
        compressed = compress_heuristic(prompt_with_code, preserve_ratio=0.5)
        
        # Code block should remain completely intact
        self.assertIn("def calculate(a, b):", compressed)
        # Critical instruction "must optimize" and "Always write" should be preserved
        self.assertIn("must optimize this code", compressed)
        self.assertIn("Always write clean variables", compressed)
        
    def test_fallback_summarizer(self):
        paragraph = (
            "PromptPilot is an AI token optimization layer that aims to reduce prompt size. "
            "It cuts down your LLM API bill by up to forty percent. "
            "It uses a local fast API backend to clean prompts dynamically. "
            "Our ultimate goal is to make AI applications affordable for developers around the world."
        )
        
        summary = fallback_summarize_paragraph(paragraph)
        
        # Fallback should trim sentences and insert placeholder
        self.assertIn("[...]", summary)
        # Should keep the first sentence
        self.assertIn("PromptPilot is an AI token optimization layer", summary)
        # Should keep the last sentence
        self.assertIn("Our ultimate goal is to make AI applications affordable", summary)

if __name__ == "__main__":
    unittest.main()
