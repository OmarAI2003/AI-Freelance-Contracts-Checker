"""Explanation Agent - Legal jargon translator

Pure LLM approach - Uses Claude's training data directly without external tools.
"""

from .agent import ExplanationAgent
from .memory_hooks import ExplanationMemoryHooks

__all__ = ['ExplanationAgent', 'ExplanationMemoryHooks']