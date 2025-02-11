"""
Main Streamlit application for PDF-to-Audio processor.
Provides user interface for uploading PDFs and controlling processing.
"""

import streamlit as st
from loguru import logger
from pathlib import Path
import json

# Use relative imports
from ..services.pdf_service import PDFService
from ..services.tts_service import TTSService
from ..core.exceptions import PDFAudioError
from ..core.llm.prompt_types import PromptType
from ..core.llm.prompts import prompts
from ..core.llm.service import create_llm_service


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    # Initialize API keys first
    if 'gemini_api_key' not in st.session_state:
        st.session_state.gemini_api_key = ""
    if 'elevenlabs_api_key' not in st.session_state:
        st.session_state.elevenlabs_api_key = ""
    if 'show_api_settings' not in st.session_state:
        st.session_state.show_api_settings = False

    # Initialize services with API keys from session state
    if 'pdf_service' not in st.session_state:
        pdf_service = PDFService()
        if st.session_state.gemini_api_key:
            pdf_service.llm_api_key = st.session_state.gemini_api_key
        st.session_state.pdf_service = pdf_service

    if 'tts_service' not in st.session_state:
        tts_service = TTSService()
        if st.session_state.elevenlabs_api_key:
            tts_service.tts_api_key = st.session_state.elevenlabs_api_key
        st.session_state.tts_service = tts_service

    # Initialize other state variables
    if 'extracted_text' not in st.session_state:
        st.session_state.extracted_text = None
    if 'analyzed_text' not in st.session_state:
        st.session_state.analyzed_text = None
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'audio_ready' not in st.session_state:
        st.session_state.audio_ready = False
    if 'audio_data' not in st.session_state:
        st.session_state.audio_data = None
    if 'timestamps' not in st.session_state:
        st.session_state.timestamps = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    if 'zoom_level' not in st.session_state:
        st.session_state.zoom_level = 0.5
    if 'auto_scroll' not in st.session_state:
        st.session_state.auto_scroll = True
    # Add AI analysis state persistence
    if 'selected_template' not in st.session_state:
        st.session_state.selected_template = None
    if 'research_area' not in st.session_state:
        st.session_state.research_area = ""
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'audio_source' not in st.session_state:
        st.session_state.audio_source = "Raw PDF Text"
    # New state variables for advanced features
    if 'chapter_breakdown' not in st.session_state:
        st.session_state.chapter_breakdown = None
    if 'study_guide' not in st.session_state:
        st.session_state.study_guide = None
    if 'bibliography' not in st.session_state:
        st.session_state.bibliography = None


def render_sidebar_config():
    """Render the configuration options in the sidebar."""
    with st.sidebar:
        st.header("Configurations")

        # API Settings Section
        st.subheader("API Settings")
        show_settings = st.toggle(
            "Show API Settings", value=st.session_state.show_api_settings)
        st.session_state.show_api_settings = show_settings

        if show_settings:
            # Gemini API Key
            gemini_key = st.text_input(
                "Gemini API Key",
                value=st.session_state.gemini_api_key,
                type="password",
                help="Enter your Google Gemini API key for text analysis"
            )
            if gemini_key != st.session_state.gemini_api_key:
                st.session_state.gemini_api_key = gemini_key
                if st.session_state.pdf_service:
                    st.session_state.pdf_service.llm_api_key = gemini_key

            # ElevenLabs API Key
            elevenlabs_key = st.text_input(
                "ElevenLabs API Key",
                value=st.session_state.elevenlabs_api_key,
                type="password",
                help="Enter your ElevenLabs API key for text-to-speech"
            )
            if elevenlabs_key != st.session_state.elevenlabs_api_key:
                st.session_state.elevenlabs_api_key = elevenlabs_key
                if st.session_state.tts_service:
                    st.session_state.tts_service.tts_api_key = elevenlabs_key

            # API Status Indicators
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                if st.session_state.gemini_api_key:
                    st.success("Gemini: ✓")
                else:
                    st.error("Gemini: ✗")
            with col2:
                if st.session_state.elevenlabs_api_key:
                    st.success("ElevenLabs: ✓")
                else:
                    st.error("ElevenLabs: ✗")

        st.divider()

        # PDF Viewer Controls
        st.subheader("PDF Controls")

        # Zoom control
        st.text("Zoom")
        zoom = st.slider(
            label="Zoom Level",
            min_value=0.1,
            max_value=2.0,
            value=st.session_state.zoom_level,
            step=0.1,
            format="%.1fx",
            label_visibility="collapsed"
        )
        st.session_state.zoom_level = zoom

        # Page control
        st.text("Page Number")
        page = st.number_input(
            label="Page Number",
            min_value=1,
            value=st.session_state.current_page,
            step=1,
            label_visibility="collapsed"
        )
        st.session_state.current_page = page

        # Auto scroll toggle
        auto_scroll = st.checkbox(
            "Auto Scroll",
            value=st.session_state.auto_scroll
        )
        st.session_state.auto_scroll = auto_scroll

        st.divider()

        # Reload button
        if st.button("Reload PDF"):
            st.rerun()


def render_pdf_viewer():
    """Render the middle PDF viewer column."""
    st.header("PDF Viewer")

    try:
        # Show PDF content if we have a processed file
        if st.session_state.processing_complete:
            # Get the page image
            image_data, (width, height) = st.session_state.pdf_service.get_page_image(
                page_number=st.session_state.current_page,
                zoom=st.session_state.zoom_level
            )

            # Display page info and navigation buttons
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("← Previous"):
                    if st.session_state.current_page > 1:
                        st.session_state.current_page -= 1
                        st.rerun()

            with col2:
                st.markdown(
                    f"Page {st.session_state.current_page} of {st.session_state.pdf_service.get_total_pages()} | Zoom: {st.session_state.zoom_level}x",
                    help="Current page and zoom level"
                )

            with col3:
                if st.button("Next →"):
                    if st.session_state.current_page < st.session_state.pdf_service.get_total_pages():
                        st.session_state.current_page += 1
                        st.rerun()

            # Display the PDF page
            st.image(image_data, use_container_width=True)

    except Exception as e:
        st.error(f"Error displaying PDF: {str(e)}")

    # File upload section below the PDF viewer
    uploaded_file = st.file_uploader(
        label="Upload a PDF file to process",
        type=['pdf'],
        help='Upload a PDF file to process'
    )

    # Process uploaded file
    if uploaded_file:
        extraction_strategy = st.selectbox(
            "Text Extraction Method",
            ["pypdf2", "llm"],
            help="Choose how to extract text from PDF"
        )

        if st.button('Process PDF'):
            try:
                with st.spinner("Processing PDF..."):
                    text = st.session_state.pdf_service.process_file(
                        file=uploaded_file,
                        extraction_strategy=extraction_strategy
                    )
                    st.session_state.extracted_text = text
                    st.session_state.processing_complete = True
                    st.success('PDF processed successfully!')
                    st.rerun()  # Refresh to show the PDF viewer
            except Exception as e:
                st.error(f'Error processing PDF: {str(e)}')


def render_ai_options():
    """Render the right AI options column."""
    st.header("AI Options")

    # Only show AI options if we have processed text
    if not st.session_state.processing_complete:
        st.info("Please process a PDF first")
        return

    # Get available templates
    templates = st.session_state.pdf_service.available_templates
    template_type = st.selectbox(
        "Analysis Template",
        options=list(templates.keys()),
        format_func=lambda x: templates[x],
        help="Choose how to analyze the text",
        key="template_select"  # Add a unique key
    )
    st.session_state.selected_template = template_type

    research_area = st.text_input(
        "Research Area",
        value=st.session_state.research_area,  # Use stored value
        help="Your specific research area for context",
        key="research_area_input"  # Add a unique key
    )
    st.session_state.research_area = research_area

    analyze_button = st.button('Analyze Text')

    # Always show the analysis section, but only populate when we have results
    if st.session_state.analysis_complete:
        st.subheader('Analysis Results')

        # If the result is a bibliography or chapter breakdown, try to parse as JSON
        if template_type in [PromptType.BIBLIOGRAPHY, PromptType.CHAPTER_BREAKDOWN]:
            try:
                result_json = json.loads(st.session_state.analyzed_text)
                st.json(result_json)
            except json.JSONDecodeError:
                # Fallback to regular text display if not valid JSON
                st.text_area(
                    label="Analysis",
                    value=st.session_state.analyzed_text,
                    height=400,
                    disabled=True,
                    label_visibility="collapsed"
                )
        else:
            # Regular text display for other analysis types
            st.text_area(
                label="Analysis",
                value=st.session_state.analyzed_text,
                height=400,
                disabled=True,
                label_visibility="collapsed"
            )

        # Special handling for chapter breakdown
        if template_type == PromptType.CHAPTER_BREAKDOWN and st.session_state.chapter_breakdown:
            try:
                chapters = json.loads(st.session_state.chapter_breakdown)
                st.subheader("Chapters")
                for idx, chapter in enumerate(chapters['chapters'], 1):
                    with st.expander(f"Chapter {idx}: {chapter['title']}"):
                        st.write("**Topics:**")
                        for topic in chapter['topics']:
                            st.write(f"- {topic}")
                        st.write("**Key Concepts:**")
                        for concept in chapter['key_concepts']:
                            st.write(f"- {concept}")
                        st.write(f"**Word Count:** {chapter['word_count']}")
            except (json.JSONDecodeError, KeyError):
                st.error("Error parsing chapter breakdown")

        # Special handling for study guide
        if template_type == PromptType.STUDY_GUIDE:
            with st.expander("Practice Questions"):
                st.write(st.session_state.analyzed_text)

        # Special handling for bibliography
        if template_type == PromptType.BIBLIOGRAPHY and st.session_state.bibliography:
            try:
                bib = json.loads(st.session_state.bibliography)
                with st.expander("Bibliography Analysis"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Most Cited Papers:**")
                        for paper in bib['analysis']['most_cited']:
                            st.write(f"- {paper}")
                    with col2:
                        st.write("**Recent Papers:**")
                        for paper in bib['analysis']['recent_papers']:
                            st.write(f"- {paper}")

                    st.write("**Key Themes:**")
                    for theme in bib['analysis']['main_themes']:
                        st.write(f"- {theme}")
            except (json.JSONDecodeError, KeyError):
                st.error("Error parsing bibliography")

    # Separate audio options section
    st.header("Audio Options")

    # Audio source selection
    st.radio(
        "Audio Source",
        ["Raw PDF Text", "Analysis Results"],
        key="audio_source",
        horizontal=True,
        index=0  # Default to Raw PDF Text
    )

    # Generate audio button - only disabled if trying to use analysis results without analysis
    audio_source = st.session_state.audio_source
    generate_audio = st.button(
        'Generate Audio',
        disabled=(
            audio_source == "Analysis Results" and not st.session_state.analysis_complete),
        help="Generate audio from the selected source"
    )

    if audio_source == "Analysis Results" and not st.session_state.analysis_complete:
        st.info("Note: Analysis Results option requires analyzing the text first")

    # Show audio section if available
    if st.session_state.audio_ready and st.session_state.audio_data:
        st.subheader('Generated Audio')
        source_text = "Analysis Results" if audio_source == "Analysis Results" else "Raw PDF Text"
        st.caption(f"Audio generated from: {source_text}")
        st.audio(st.session_state.audio_data, format='audio/mp3')
        st.download_button(
            label="Download Audio",
            data=st.session_state.audio_data,
            file_name="audio.mp3",
            mime="audio/mp3"
        )

    if analyze_button or generate_audio:
        try:
            # Handle analysis button click
            if analyze_button:
                with st.spinner("Analyzing text..."):
                    analyzed_text = st.session_state.pdf_service.analyze_text(
                        text=st.session_state.extracted_text,
                        template_type=template_type,
                        research_area=research_area
                    )
                    st.session_state.analyzed_text = analyzed_text
                    st.session_state.analysis_complete = True

                    # Store structured results if applicable
                    if template_type == PromptType.CHAPTER_BREAKDOWN:
                        try:
                            # Validate JSON before storing
                            json.loads(analyzed_text)
                            st.session_state.chapter_breakdown = analyzed_text
                        except json.JSONDecodeError:
                            st.warning(
                                "Chapter breakdown result is not in valid JSON format")
                            st.session_state.chapter_breakdown = None
                    elif template_type == PromptType.BIBLIOGRAPHY:
                        try:
                            # Validate JSON before storing
                            json.loads(analyzed_text)
                            st.session_state.bibliography = analyzed_text
                        except json.JSONDecodeError:
                            st.warning(
                                "Bibliography result is not in valid JSON format")
                            st.session_state.bibliography = None
                    elif template_type == PromptType.STUDY_GUIDE:
                        st.session_state.study_guide = analyzed_text

                    st.rerun()  # Refresh to show updated analysis

            # Handle audio generation separately
            if generate_audio:
                try:
                    logger.info("Starting audio generation")
                    with st.spinner("Converting to audio..."):
                        # Select text based on audio source
                        text_for_audio = (
                            st.session_state.analyzed_text
                            if audio_source == "Analysis Results" and st.session_state.analysis_complete
                            else st.session_state.extracted_text
                        )

                        if text_for_audio is None:
                            st.error(
                                "No text available for audio generation. Please process a PDF first.")
                            return

                        audio_data, timestamps = st.session_state.tts_service.text_to_audio(
                            text=text_for_audio,
                            with_timestamps=True
                        )
                        st.session_state.audio_ready = True
                        st.session_state.audio_data = audio_data
                        st.session_state.timestamps = timestamps
                        st.rerun()  # Refresh to show audio player

                except Exception as e:
                    logger.error(f"Error generating audio: {str(e)}")
                    st.error(f'Error generating audio: {str(e)}')

        except Exception as e:
            st.error(f'Error during operation: {str(e)}')


def main():
    """Main Streamlit application."""
    # Custom CSS to match dark theme and compact layout
    st.markdown("""
        <style>
            /* Global styles */
            .stApp {
                background-color: rgb(17, 24, 39); /* bg-gray-900 */
            }

            /* Remove default Streamlit padding */
            .main .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
                max-width: none;
            }

            /* Hide main header */
            header[data-testid="stHeader"] {
                display: none;
            }

            div[data-testid="stToolbar"],
            div[data-testid="stDecoration"],
            #MainMenu,
            header,
            footer {
                display: none;
            }

            /* Headers styling */
            h1, h2, h3 {
                color: white;
                font-weight: 600; /* font-semibold */
                padding: 0.5rem 0;
                margin: 0;
            }

            /* Column styling */
            [data-testid="column"] {
                background-color: rgb(31, 41, 55); /* bg-gray-800 */
                border-radius: 0.5rem; /* rounded-lg */
                padding: 1rem; /* p-4 */
            }

            /* Sidebar styling */
            [data-testid="stSidebar"] {
                background-color: rgb(31, 41, 55); /* bg-gray-800 */
                padding: 1rem;
            }
            [data-testid="stSidebar"] [data-testid="stMarkdown"] {
                color: white;
            }

            /* Stmarkdown and block container */
            .stMarkdown {
                min-height: 0;
            }
            .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
                max-width: none;
            }

            /* Remove decorative elements */
            div[data-testid="stDecoration"] {
                display: none;
            }

            /* Column gap and spacing control */
            div.st-emotion-cache-ocqkz7 {
                gap: 1rem !important;
                padding: 0 !important;
            }
            div.st-emotion-cache-ocqkz7 > div {
                flex: 1 1 0% !important;
            }
            [data-testid="column"] + [data-testid="column"] {
                margin-left: 0 !important;
            }

            /* File uploader styling */
            .stFileUploader > div {
                background-color: rgb(55, 65, 81); /* bg-gray-700 */
                border: 2px dashed rgb(75, 85, 99); /* border-2 border-dashed border-gray-600 */
                padding: 1rem;
                border-radius: 0.5rem;
            }
            .stFileUploader > div:hover {
                background-color: rgb(55, 65, 81);
                border-color: rgb(107, 114, 128); /* border-gray-500 */
            }

            /* Button styling */
            .stButton > button {
                background-color: rgb(37, 99, 235); /* bg-blue-600 */
                color: white;
                border: none;
                padding: 0.5rem 1rem;
                border-radius: 0.25rem;
                width: 100%;
            }
            .stButton > button:hover {
                background-color: rgb(59, 130, 246); /* bg-blue-500 */
            }
            .stButton > button[data-baseweb="button"][kind="primary"] {
                background-color: rgb(22, 163, 74); /* bg-green-600 */
            }
            .stButton > button[data-baseweb="button"][kind="primary"]:hover {
                background-color: rgb(34, 197, 94); /* bg-green-500 */
            }

            /* Input styling */
            .stTextInput > div > div > input,
            .stNumberInput > div > div > input {
                background-color: rgb(55, 65, 81); /* bg-gray-700 */
                color: white;
                border: none;
                padding: 0.5rem;
                border-radius: 0.25rem;
            }

            /* Slider styling */
            .stSlider > div > div {
                background-color: rgb(55, 65, 81); /* bg-gray-700 */
            }
            .stSlider > div > div > div[role="slider"] {
                background-color: rgb(37, 99, 235); /* bg-blue-600 */
            }

            /* Text area styling */
            .stTextArea > div > div > textarea {
                background-color: rgb(55, 65, 81); /* bg-gray-700 */
                color: white;
                border: none;
                padding: 0.5rem;
                border-radius: 0.25rem;
                min-height: 8rem; /* h-32 */
            }

            /* Checkbox styling */
            .stCheckbox > label > div[role="checkbox"] {
                background-color: rgb(55, 65, 81); /* bg-gray-700 */
                border: none;
            }
            .stCheckbox > label > div[role="checkbox"][data-checked="true"] {
                background-color: rgb(37, 99, 235); /* bg-blue-600 */
            }

            /* Select box styling */
            .stSelectbox > div > div {
                background-color: rgb(55, 65, 81); /* bg-gray-700 */
                border: none;
                border-radius: 0.25rem;
            }
            .stSelectbox > div > div > div {
                background-color: rgb(55, 65, 81); /* bg-gray-700 */
                color: white;
            }

            /* Warning text */
            .stAlert {
                background-color: transparent;
                color: rgb(250, 204, 21); /* text-yellow-400 */
            }

            /* Horizontal lines */
            hr {
                border-color: rgb(75, 85, 99); /* border-gray-600 */
                margin: 1rem 0;
            }
        </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    initialize_session_state()

    # Render sidebar configuration
    render_sidebar_config()

    # Create two columns with specific ratios for the main content
    # Using relative numbers where the middle takes 70% and right 30%
    viewer_col, ai_col = st.columns(
        [7, 3], gap="small")

    # Use the columns
    with viewer_col:
        render_pdf_viewer()

    with ai_col:
        render_ai_options()


if __name__ == "__main__":
    main()
