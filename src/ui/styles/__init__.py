import streamlit as st

def load_styles():
    """Load and apply CSS styles."""
    with open('src/ui/styles/main.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
