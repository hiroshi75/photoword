import streamlit as st
from streamlit_float import float_init, float_box

def test_imports():
    print("Testing streamlit-float imports...")
    print("✓ Successfully imported streamlit-float")
    print(f"Location: {float_init.__module__}")
    print(f"Version: {float_box.__module__}")

if __name__ == "__main__":
    test_imports()
