"""
Defines the types of prompts available in the system.
"""

from enum import Enum


class PromptType(Enum):
    """Types of available prompts."""
    TEXT_EXTRACTION = "text_extraction"
    RESEARCH_SUMMARY = "research_summary"
    METHODOLOGY_ANALYSIS = "methodology_analysis"
    LITERATURE_REVIEW = "literature_review"
    KEY_FINDINGS = "key_findings"
    CRITICAL_ANALYSIS = "critical_analysis"
    FUTURE_RESEARCH = "future_research"
    QUICK_REVIEW = "quick_review"
    BIBLIOGRAPHY = "bibliography"
