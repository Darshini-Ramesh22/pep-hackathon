"""
Streamlit Cloud Entry Point for Campaign Brain
This file is the entry point for Streamlit Community Cloud deployment.
"""
import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: F401 - required by dashboard mock data
from ui.dashboard import main

main()
