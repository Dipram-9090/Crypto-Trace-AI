"""
CryptoTrace AI - Frontend Entrypoint.
Launches the full interactive Streamlit Forensic Analytics Dashboard.
"""

import sys
import os

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dashboard.app import main

if __name__ == "__main__":
    main()
