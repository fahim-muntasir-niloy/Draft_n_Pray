#!/usr/bin/env python3
"""
Launcher for Draft 'n' Pray Streamlit UI
"""

import subprocess
import sys
import os


def main():
    """Launch the Streamlit app"""
    try:
        # Change to the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)

        # Run streamlit without specifying port to avoid conflicts
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                "streamlit_app.py",
            ]
        )
    except KeyboardInterrupt:
        print("\n👋 Streamlit app stopped by user")
    except Exception as e:
        print(f"❌ Error running Streamlit app: {e}")


if __name__ == "__main__":
    main()
