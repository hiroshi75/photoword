import sys
import importlib.util

def check_environment():
    print(f"Python executable: {sys.executable}\n")
    print("Python path:")
    for path in sys.path:
        print(f"  {path}")
    
    print("\nChecking streamlit_float installation:")
    try:
        import streamlit_float
        print("✓ streamlit_float successfully imported")
        print(f"Version: {streamlit_float.__version__}")
        print(f"Location: {importlib.util.find_spec('streamlit_float').origin}")
    except ImportError as e:
        print(f"✗ Failed to import streamlit_float: {str(e)}")

if __name__ == "__main__":
    check_environment()
