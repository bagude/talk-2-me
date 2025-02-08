"""
Prompt template system for managing LLM prompts.
Provides structured templates for different use cases.
"""

from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum
import json

from loguru import logger


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


@dataclass
class PromptTemplate:
    """Template for LLM prompts with metadata."""
    template: str
    description: str
    examples: list[dict] = None
    parameters: dict = None

    def format(self, **kwargs: Any) -> str:
        """Format the template with provided parameters."""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing required parameter: {e}")
            raise ValueError(f"Missing required parameter: {e}")


class PromptLibrary:
    """Library of prompt templates for different use cases."""

    def __init__(self):
        """Initialize prompt library with research-focused templates."""
        self._templates: Dict[PromptType, PromptTemplate] = {
            PromptType.RESEARCH_SUMMARY: PromptTemplate(
                template="""
                Create a comprehensive research summary following this structure:
                1. Core Research Question/Hypothesis
                   - What is the main research question?
                   - What are the hypotheses being tested?

                2. Key Theoretical Framework
                   - What theories are being used/tested?
                   - How does this fit into the broader field?

                3. Methodology Highlights
                   - Key methodological approaches
                   - Sample size and characteristics
                   - Notable analytical techniques

                4. Principal Findings
                   - Major results and their significance
                   - Statistical relevance if applicable
                   - Key tables/figures and their implications

                5. Critical Implications
                   - Theoretical contributions
                   - Practical applications
                   - Limitations and future research

                6. Relevance to Your Field
                   - How this connects to {research_area}
                   - Potential applications to your work

                Format the output in clear, concise sections that are easy to follow when converted to audio.
                Focus on aspects most relevant to {research_area}.
                
                Document to analyze:
                {content}
                """.strip(),
                description="Creates a structured research summary with field-specific focus",
                parameters={
                    "content": "The paper to analyze",
                    "research_area": "Your specific research area/focus"
                }
            ),

            PromptType.METHODOLOGY_ANALYSIS: PromptTemplate(
                template="""
                Analyze the research methodology with a focus on replication and application:

                1. Research Design
                   - Type of study (experimental, observational, etc.)
                   - Key variables and their operationalization
                   - Control measures and potential confounds

                2. Data Collection
                   - Methods used
                   - Sample characteristics
                   - Timeline and procedures
                   - Notable instruments or tools

                3. Analysis Techniques
                   - Statistical methods employed
                   - Software or tools used
                   - Robustness checks
                   - Validity considerations

                4. Methodological Strengths
                   - What was done particularly well?
                   - Novel approaches or innovations

                5. Limitations and Considerations
                   - Potential methodological weaknesses
                   - Areas for improvement
                   - What to consider when replicating

                6. Application to Your Research
                   - How could you adapt this methodology?
                   - Potential improvements for your context
                   - Resource requirements

                Focus on practical details that would be useful for replication or adaptation.
                
                Document to analyze:
                {content}
                """.strip(),
                description="Detailed analysis of research methodology for potential replication",
                parameters={"content": "The methodology to analyze"}
            ),

            PromptType.QUICK_REVIEW: PromptTemplate(
                template="""
                Create a 5-minute executive summary of this research paper:

                1. One-Sentence Overview
                   - Core research question and main finding

                2. Why It Matters
                   - Key contribution to the field
                   - Practical implications

                3. Essential Methods
                   - Core methodology in simple terms
                   - Key analytical approach

                4. Critical Findings
                   - Most important results
                   - Surprising or controversial aspects

                5. Your Next Steps
                   - How this connects to your research
                   - Action items or follow-up needed

                Keep it concise and focused on decision-making points.
                Highlight anything that needs immediate attention or follow-up.
                
                Document to review:
                {content}
                """.strip(),
                description="Quick, actionable summary for busy researchers",
                parameters={"content": "The paper to review"}
            ),

            PromptType.LITERATURE_REVIEW: PromptTemplate(
                template="""
                Create a literature review analysis focusing on how this paper fits into the broader research landscape:

                1. Research Stream Identification
                   - Which research stream(s) does this belong to?
                   - Key theoretical frameworks used

                2. Historical Context
                   - How this builds on previous work
                   - Major works cited and their relevance
                   - Evolution of the research question

                3. Current Debates
                   - Controversial or contested areas
                   - Different schools of thought
                   - Where this paper stands

                4. Research Gaps
                   - What gaps does this address?
                   - What remains unexplored?
                   - Potential future directions

                5. Connection Map
                   - Links to other key papers in {research_area}
                   - Theoretical or methodological connections
                   - Potential synthesis opportunities

                6. Integration Points
                   - How to integrate with your research
                   - Potential citation purposes
                   - Critical discussion points

                Focus on building a mental map of how this fits into your research narrative.
                
                Document to analyze:
                {content}
                """.strip(),
                description="Analyzes paper's place in literature and research landscape",
                parameters={
                    "content": "The paper to analyze",
                    "research_area": "Your specific research area"
                }
            ),

            PromptType.BIBLIOGRAPHY: PromptTemplate(
                template="""
                Extract and analyze the bibliography in JSON format:

                1. First, extract all references and format them as a JSON array
                2. For each reference, include:
                   - Full citation
                   - Authors
                   - Year
                   - Title
                   - Journal/Source
                   - DOI if available
                   - Type (empirical, theoretical, review, etc.)
                   - Relevance to {research_area}
                   - Key themes or topics
                3. Identify the most cited works
                4. Highlight seminal papers
                5. Note any recent (last 2 years) references

                Format the output as valid JSON for easy parsing.
                
                Document to analyze:
                {content}
                """.strip(),
                description="Extracts and analyzes bibliography with research context",
                parameters={
                    "content": "The paper to analyze",
                    "research_area": "Your specific research area"
                }
            ),
        }

    def get_template(self, prompt_type: PromptType) -> PromptTemplate:
        """Get a prompt template by type."""
        if prompt_type not in self._templates:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        return self._templates[prompt_type]

    def add_template(self, prompt_type: PromptType, template: PromptTemplate) -> None:
        """Add or update a prompt template."""
        self._templates[prompt_type] = template

    def list_templates(self) -> Dict[PromptType, str]:
        """List available templates and their descriptions."""
        return {
            PromptType.RESEARCH_SUMMARY: "Comprehensive research summary with key findings",
            PromptType.METHODOLOGY_ANALYSIS: "Detailed analysis of research methodology",
            PromptType.QUICK_REVIEW: "Quick, actionable summary for busy researchers",
            PromptType.LITERATURE_REVIEW: "Analysis of paper's place in research landscape",
            PromptType.BIBLIOGRAPHY: "Extract and analyze bibliography in JSON format",
            PromptType.KEY_FINDINGS: "Extract key findings and contributions",
            PromptType.CRITICAL_ANALYSIS: "Critical analysis of strengths and weaknesses",
            PromptType.FUTURE_RESEARCH: "Identify future research directions",
        }


# Global prompt library instance
prompts = PromptLibrary()
