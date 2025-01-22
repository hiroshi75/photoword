import subprocess
import time
import signal
import os

def run_test():
    """
    Test CTRL+C handling in the Streamlit app.
    Returns True if the app terminates properly, False otherwise.
    """
    print("Starting Streamlit app...")
    process = subprocess.Popen(["streamlit", "run", "test_ctrl_c.py"])
    
    print("Waiting 10 seconds for app to initialize...")
    time.sleep(10)
    
    print("Sending CTRL+C (SIGINT)...")
    process.send_signal(signal.SIGINT)
    
    print("Waiting for process to terminate...")
    try:
        process.wait(timeout=5)
        print("Process terminated successfully")
        return True
    except subprocess.TimeoutExpired:
        print("Process failed to terminate within timeout")
        process.kill()
        return False

if __name__ == "__main__":
    success = run_test()
    exit(0 if success else 1)
