"""
Entry point for the Streamlit application.
This file ensures proper package imports when running with Streamlit.
"""

import streamlit.web.bootstrap
from pathlib import Path

if __name__ == "__main__":
    app_path = Path(__file__).parent / "src" / "ui" / "app.py"
    streamlit.web.bootstrap.run(str(app_path), "", [], [])
