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
    CHAPTER_BREAKDOWN = "chapter_breakdown"
    STUDY_GUIDE = "study_guide"
    APA_CITATION = "apa_citation"


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
            PromptType.TEXT_EXTRACTION: PromptTemplate(
                template="""
                Extract and structure the text content from this document.
                Preserve the logical flow and hierarchy of information.
                Maintain section headers, lists, and important formatting.
                Remove any non-essential formatting or artifacts.
                Ensure the output is clean, readable text suitable for further analysis.

                Focus on:
                - Main content and arguments
                - Section structure and flow
                - Lists and enumerations
                - Tables and figures (describe their content)
                - Citations and references
                
                Document to process:
                {content}
                """.strip(),
                description="Extracts clean, structured text from documents",
                parameters={"content": "The document to process"}
            ),

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

            PromptType.KEY_FINDINGS: PromptTemplate(
                template="""
                Extract and analyze the key findings from this research:

                1. Primary Results
                   - Main discoveries and insights
                   - Statistical significance
                   - Effect sizes and magnitudes
                   - Unexpected findings

                2. Supporting Evidence
                   - Data and measurements
                   - Validation methods
                   - Replication results
                   - Control comparisons

                3. Practical Significance
                   - Real-world implications
                   - Application potential
                   - Industry relevance
                   - Policy impacts

                4. Theoretical Contributions
                   - New concepts introduced
                   - Theoretical validations
                   - Challenges to existing theory
                   - Framework extensions

                5. Methodological Innovations
                   - Novel approaches
                   - Technical advances
                   - Measurement improvements
                   - Analysis innovations

                6. Relevance to {research_area}
                   - Direct applications
                   - Adaptation potential
                   - Integration opportunities

                Prioritize findings that are statistically significant, novel, and impactful.
                
                Document to analyze:
                {content}
                """.strip(),
                description="Extracts and analyzes key research findings",
                parameters={
                    "content": "The paper to analyze",
                    "research_area": "Your specific research area"
                }
            ),

            PromptType.CRITICAL_ANALYSIS: PromptTemplate(
                template="""
                Provide a critical analysis of this research:

                1. Theoretical Framework
                   - Appropriateness of theories used
                   - Completeness of framework
                   - Alternative theoretical perspectives
                   - Integration with existing literature

                2. Methodology Assessment
                   - Research design strengths/weaknesses
                   - Sample selection and size
                   - Control of variables
                   - Measurement validity and reliability

                3. Analysis Rigor
                   - Statistical approach appropriateness
                   - Data handling procedures
                   - Assumption validation
                   - Alternative explanations considered

                4. Results Interpretation
                   - Strength of conclusions
                   - Causality claims
                   - Generalizability
                   - Practical significance

                5. Limitations Analysis
                   - Design constraints
                   - Implementation challenges
                   - Generalizability limits
                   - Resource constraints

                6. Impact Assessment
                   - Contribution to {research_area}
                   - Practical applications
                   - Policy implications
                   - Future research value

                Be constructively critical while acknowledging strengths.
                
                Document to analyze:
                {content}
                """.strip(),
                description="Provides critical analysis of research strengths and weaknesses",
                parameters={
                    "content": "The paper to analyze",
                    "research_area": "Your specific research area"
                }
            ),

            PromptType.METHODOLOGY_ANALYSIS: PromptTemplate(
                template="""
                Provide a detailed analysis of the research methodology:

                1. Research Design
                   - Type of study(experimental, observational, etc.)
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
                You are an expert scientific researcher who has years of experience in conducting systematic literature surveys and meta-analyses of different topics. You pride yourself on incredible accuracy and attention to detail. You always stick to the facts in the sources provided, and never make up new facts.

                Now look at the research paper below, and answer the following questions in 1-2 sentences.

                When was the paper published?

                What is the sample size?

                What is the study methodology? in particular, is it a randomized control trial?

                How was the study funded? in particular, was the funding from commercial funders?

                What was the key question being studied?

                What were the key findings to the key question being studied?

                Paper to analyze:
                {content}
                """.strip(),
                description="Provides quick, focused analysis of key aspects of a research paper",
                parameters={"content": "The paper to analyze"}
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
                Extract and analyze the bibliography in strict JSON format:

                {
                    "references": [
                        {
                            "citation": "Full citation text",
                            "authors": ["Author 1", "Author 2"],
                            "year": 2024,
                            "title": "Paper title",
                            "journal": "Journal name",
                            "doi": "DOI if available",
                            "type": "empirical|theoretical|review",
                            "relevance": "Relevance to {research_area}",
                            "themes": ["theme1", "theme2"],
                            "is_seminal": true|false,
                            "citation_count": "if available",
                            "is_recent": true|false
                        }
                    ],
                    "analysis": {
                        "most_cited": ["ref1", "ref2"],
                        "seminal_works": ["ref1", "ref2"],
                        "recent_papers": ["ref1", "ref2"],
                        "key_journals": ["journal1", "journal2"],
                        "main_themes": ["theme1", "theme2"]
                    }
                }

                Rules:
                1. Extract ALL references from the document
                2. Format exactly as shown above
                3. Ensure valid JSON structure
                4. Mark papers from last 2 years as recent
                5. Identify seminal papers based on citation patterns
                6. Group by research themes
                7. Note relevance to {research_area}

                Document to analyze:
                {content}
                """.strip(),
                description="Extracts and analyzes bibliography in structured JSON format",
                parameters={
                    "content": "The paper to analyze",
                    "research_area": "Your specific research area"
                }
            ),

            PromptType.FUTURE_RESEARCH: PromptTemplate(
                template="""
                Identify and analyze future research directions based on this paper:

                1. Direct Extensions
                   - Immediate next steps suggested by authors
                   - Natural extensions of current findings
                   - Methodological improvements

                2. Research Gaps
                   - Unexplored aspects of the topic
                   - Limitations that need addressing
                   - Missing variables or contexts

                3. Emerging Opportunities
                   - New technologies or methods that could be applied
                   - Interdisciplinary connections
                   - Potential paradigm shifts

                4. Practical Applications
                   - Industry or field applications to explore
                   - Policy implications to investigate
                   - Implementation studies needed

                5. Your Research Context
                   - Specific opportunities in {research_area}
                   - How to build on this work
                   - Potential collaboration points

                6. Resource Considerations
                   - Required skills or expertise
                   - Potential funding sources
                   - Timeline and scope estimates

                Focus on actionable research directions that align with current trends and needs.

                Document to analyze:
                {content}
                """.strip(),
                description="Identifies future research directions and opportunities",
                parameters={
                    "content": "The paper to analyze",
                    "research_area": "Your specific research area"
                }
            ),

            PromptType.CHAPTER_BREAKDOWN: PromptTemplate(
                template="""
                Analyze this document and create a logical chapter breakdown:

                1. Document Structure Analysis
                   - Identify major sections and subsections
                   - Detect natural topic transitions
                   - Recognize hierarchical structure

                2. Chapter Identification
                   - Create logical chapter divisions
                   - Maintain content coherence
                   - Preserve academic flow

                3. For each chapter/section:
                   - Title/heading
                   - Main topics covered
                   - Key concepts introduced
                   - Important figures/tables
                   - Word count and density
                   - Logical connections to other chapters

                4. Navigation Markers
                   - Clear start/end points
                   - Transition phrases
                   - Cross-references

                Format the output as a structured JSON:
                {{
                    "chapters": [
                        {{
                            "title": "Chapter title",
                            "start_marker": "Text that starts this chapter",
                            "end_marker": "Text that ends this chapter",
                            "topics": ["topic1", "topic2"],
                            "key_concepts": ["concept1", "concept2"],
                            "word_count": 1234,
                            "references": ["ref1", "ref2"]
                        }}
                    ]
                }}

                Document to analyze:
                {content}
                """.strip(),
                description="Creates logical chapter breakdown with navigation markers",
                parameters={"content": "The document to analyze"}
            ),

            PromptType.STUDY_GUIDE: PromptTemplate(
                template="""
                Create a comprehensive study guide for this document:

                1. Learning Objectives
                   - Core concepts to master
                   - Key skills to develop
                   - Understanding checkpoints

                2. Key Concepts
                   - Define main terms
                   - Explain core theories
                   - Illustrate key relationships
                   - Highlight critical formulas/methods

                3. Summary Points
                   - Chapter/section summaries
                   - Main arguments/findings
                   - Important evidence
                   - Methodology highlights

                4. Practice Questions
                   - Conceptual understanding questions
                   - Application scenarios
                   - Critical thinking exercises
                   - Self-assessment prompts

                5. Study Resources
                   - Related readings
                   - Additional references
                   - Online resources
                   - Practice materials

                Format as a structured guide optimized for learning.
                Include both theoretical understanding and practical application.

                Document to analyze:
                {content}
                """.strip(),
                description="Generates comprehensive study guide with practice materials",
                parameters={"content": "The document to analyze"}
            ),

            PromptType.APA_CITATION: PromptTemplate(
                template="""
                Generate an APA citation in structured JSON format for the given content.
                The output should strictly follow this JSON schema:
                {
                  "annotatedBibliography": [
                    {
                      "author": "Last names and initials (e.g., 'Smith, J. D. & Doe, A. B.')",
                      "year": "Publication year",
                      "title": "Full title of the work",
                      "publisher": "Publisher name or journal title",
                      "doi_url": "DOI URL if available",
                      "publication_type": "Type (e.g., journal article, book, etc.)",
                      "volume": "Volume number if applicable",
                      "issue": "Issue number if applicable",
                      "pages": "Page range if applicable"
                    }
                  ]
                }

                Ensure:
                - All author names are properly formatted with last name, first initial
                - Multiple authors are connected with '&'
                - Title is in sentence case
                - All required fields are filled based on the source type
                - JSON is properly formatted and valid
                - Include DOI URL if available

                - If any content is missing or not clear, return an empty JSON object

                Content to cite:
                {content}
                """.strip(),
                description="Generates structured JSON format APA citations",
                parameters={
                    "content": "The source content to create a citation for"
                }
            )
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
            PromptType.TEXT_EXTRACTION: "Extract clean, structured text from documents",
            PromptType.RESEARCH_SUMMARY: "Comprehensive research summary with key findings",
            PromptType.METHODOLOGY_ANALYSIS: "Detailed analysis of research methodology",
            PromptType.QUICK_REVIEW: "Quick, actionable summary for busy researchers",
            PromptType.LITERATURE_REVIEW: "Analysis of paper's place in research landscape",
            PromptType.BIBLIOGRAPHY: "Extract and analyze bibliography in structured JSON format",
            PromptType.KEY_FINDINGS: "Extract key findings and contributions",
            PromptType.CRITICAL_ANALYSIS: "Critical analysis of strengths and weaknesses",
            PromptType.FUTURE_RESEARCH: "Identify future research directions",
            PromptType.CHAPTER_BREAKDOWN: "Create logical chapter breakdown with navigation markers",
            PromptType.STUDY_GUIDE: "Generate comprehensive study guide with practice materials",
        }


# Global prompt library instance
prompts = PromptLibrary()
