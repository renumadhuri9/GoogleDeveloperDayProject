import streamlit as st
import os
import sys

if __name__ == "__main__":
    # Run the Streamlit app
    os.system(f"streamlit run {os.path.join(os.path.dirname(__file__), 'server.py')}")