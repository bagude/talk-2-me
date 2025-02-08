"""
Main Streamlit application for PDF-to-Audio processor.
Provides user interface for uploading PDFs and controlling processing.
"""

import streamlit as st
from loguru import logger
from pathlib import Path

# Use absolute imports since Streamlit runs this file directly
from src.services.pdf_service import PDFService
from src.services.tts_service import TTSService
from src.core.exceptions import PDFAudioError
from src.core.llm.prompt_types import PromptType
from src.core.llm.prompts import prompts
from src.core.llm.service import create_llm_service


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'pdf_service' not in st.session_state:
        st.session_state.pdf_service = PDFService()
    if 'tts_service' not in st.session_state:
        st.session_state.tts_service = TTSService()
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


def render_sidebar():
    """Render the sidebar with configuration options."""
    st.sidebar.title("Configuration")

    # Extraction strategy
    strategy = st.sidebar.selectbox(
        "Text Extraction Method",
        ["pypdf2", "llm"],
        help="Choose how to extract text from PDF"
    )

    return strategy


def render_llm_options():
    """Render LLM processing options."""
    st.sidebar.subheader("LLM Processing")

    # Get available templates from session state
    templates = st.session_state.pdf_service.available_templates
    template_name = st.sidebar.selectbox(
        "Analysis Template",
        list(templates.keys()),
        format_func=lambda x: templates[x],
        help="Choose how to analyze the PDF"
    )
    template_type = PromptType[template_name]

    # Research area input
    research_area = st.sidebar.text_input(
        "Research Area",
        help="Your specific research area for context"
    )

    return template_type, research_area


def handle_pdf_upload():
    """Handle PDF file upload and processing."""
    st.header('Upload PDF')

    # Basic extraction method selection
    extraction_strategy = st.sidebar.selectbox(
        "Text Extraction Method",
        ["pypdf2", "llm"],
        help="Choose how to extract text from PDF"
    )

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help='Upload a PDF file to process'
    )

    if uploaded_file and st.button('Extract Text'):
        try:
            with st.spinner("Extracting text from PDF..."):
                text = st.session_state.pdf_service.process_file(
                    file=uploaded_file,
                    extraction_strategy=extraction_strategy
                )
                st.session_state.extracted_text = text
                st.session_state.processing_complete = True
                st.success('Text extracted successfully!')

        except Exception as e:
            st.error(f'Error extracting text: {str(e)}')
            return

    # Show analysis options only after text is extracted
    if st.session_state.processing_complete:
        st.header('Analyze Text')

        col1, col2 = st.columns([2, 1])
        with col1:
            # Get available templates
            templates = st.session_state.pdf_service.available_templates
            template_type = st.selectbox(
                "Choose Analysis Type",
                options=list(templates.keys()),
                format_func=lambda x: templates[x],
                help="Choose how to analyze the text"
            )

        with col2:
            research_area = st.text_input(
                "Research Area",
                help="Your specific research area for context"
            )

        analyze_button = st.button('Analyze')
        generate_audio = st.button('Analyze and Generate Audio')

        if analyze_button or generate_audio:
            try:
                with st.spinner("Analyzing text..."):
                    analyzed_text = st.session_state.pdf_service.analyze_text(
                        text=st.session_state.extracted_text,
                        template_type=template_type,
                        research_area=research_area
                    )
                    st.session_state.analyzed_text = analyzed_text
                    st.success('Analysis complete!')

                    # Display analysis results
                    st.header('Analysis Results')
                    st.text_area(
                        "Analysis",
                        analyzed_text,
                        height=300,
                        disabled=True
                    )

                    # Generate audio if requested
                    if generate_audio:
                        try:
                            logger.info("Starting audio generation")
                            with st.spinner("Converting to audio..."):
                                logger.debug(
                                    f"Converting text of length {len(analyzed_text)} to audio")
                                audio_data, timestamps = st.session_state.tts_service.text_to_audio(
                                    text=analyzed_text,
                                    with_timestamps=True
                                )
                                st.session_state.audio_ready = True
                                st.session_state.audio_data = audio_data
                                st.session_state.timestamps = timestamps

                                # Display audio section
                                st.header('Generated Audio')
                                st.audio(audio_data, format='audio/mp3')
                                st.download_button(
                                    label="Download Audio",
                                    data=audio_data,
                                    file_name="analysis.mp3",
                                    mime="audio/mp3"
                                )
                                st.success('Audio generated successfully!')

                        except Exception as e:
                            logger.error(f"Error generating audio: {str(e)}")
                            logger.exception("Full traceback:")
                            st.error(f'Error generating audio: {str(e)}')

            except Exception as e:
                st.error(f'Error during analysis: {str(e)}')


def main():
    """Main Streamlit application."""
    st.title('PDF to Audio Processor')

    # Initialize session state
    initialize_session_state()

    # Handle PDF upload and processing
    handle_pdf_upload()

    # Display results
    if st.session_state.processing_complete:
        st.header('Extracted Text')
        with st.expander("Show extracted text", expanded=True):
            st.text_area(
                "Content",
                st.session_state.extracted_text,
                height=300,
                disabled=True
            )

        # Clear button
        if st.button('Clear'):
            st.session_state.pdf_service.clear()
            st.session_state.extracted_text = None
            st.session_state.processing_complete = False
            st.rerun()


if __name__ == "__main__":
    main()
