"""
Analysis Agent for AI Freelance Contracts Checker

This module contains the Analysis Agent that detects unfair contract clauses
and assigns risk levels to freelance contracts.
"""

from .agent import AnalysisAgent
from .tools import contract_parser, jurisdiction_checker

__all__ = ['AnalysisAgent', 'contract_parser', 'jurisdiction_checker']
