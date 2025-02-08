"""
Test suite for prompt template system.
"""

import pytest
from src.core.llm.prompts import (
    PromptType,
    PromptTemplate,
    PromptLibrary,
    prompts
)


@pytest.fixture
def test_template():
    """Create a test template."""
    return PromptTemplate(
        template="Analyze this: {content} for {research_area}",
        description="Test template",
        parameters={
            "content": "Content to analyze",
            "research_area": "Research area"
        }
    )


def test_prompt_template_format(test_template):
    """Test template formatting."""
    result = test_template.format(
        content="test content",
        research_area="AI"
    )
    assert result == "Analyze this: test content for AI"


def test_prompt_template_missing_parameter(test_template):
    """Test template with missing parameter."""
    with pytest.raises(ValueError, match="Missing required parameter"):
        test_template.format(content="test content")


def test_prompt_library_get_template():
    """Test getting templates from library."""
    template = prompts.get_template(PromptType.RESEARCH_SUMMARY)
    assert isinstance(template, PromptTemplate)
    assert "research summary" in template.description.lower()


def test_prompt_library_invalid_type():
    """Test getting invalid template type."""
    with pytest.raises(ValueError, match="Unknown prompt type"):
        prompts.get_template("invalid_type")


def test_prompt_library_add_template(test_template):
    """Test adding new template to library."""
    library = PromptLibrary()
    library.add_template(PromptType.QUICK_REVIEW, test_template)

    retrieved = library.get_template(PromptType.QUICK_REVIEW)
    assert retrieved == test_template


def test_prompt_library_list_templates():
    """Test listing available templates."""
    templates = prompts.list_templates()
    assert isinstance(templates, dict)
    assert "RESEARCH_SUMMARY" in templates
    assert "BIBLIOGRAPHY" in templates


def test_research_summary_template():
    """Test research summary template formatting."""
    template = prompts.get_template(PromptType.RESEARCH_SUMMARY)
    result = template.format(
        content="Sample paper content",
        research_area="Machine Learning"
    )
    assert "Machine Learning" in result
    assert "Sample paper content" in result
    assert "Core Research Question" in result


def test_bibliography_template():
    """Test bibliography template JSON guidance."""
    template = prompts.get_template(PromptType.BIBLIOGRAPHY)
    result = template.format(
        content="Sample bibliography",
        research_area="Data Science"
    )
    assert "JSON" in result
    assert "Data Science" in result
    assert "array" in result.lower()


def test_quick_review_template():
    """Test quick review template structure."""
    template = prompts.get_template(PromptType.QUICK_REVIEW)
    result = template.format(content="Sample paper")
    assert "5-minute" in result
    assert "One-Sentence Overview" in result
    assert "Next Steps" in result


def test_methodology_analysis_template():
    """Test methodology analysis template sections."""
    template = prompts.get_template(PromptType.METHODOLOGY_ANALYSIS)
    result = template.format(content="Sample methodology")
    assert "Research Design" in result
    assert "Data Collection" in result
    assert "Analysis Techniques" in result


def test_literature_review_template():
    """Test literature review template context."""
    template = prompts.get_template(PromptType.LITERATURE_REVIEW)
    result = template.format(
        content="Sample literature",
        research_area="NLP"
    )
    assert "Research Stream" in result
    assert "Historical Context" in result
    assert "NLP" in result
