import streamlit as st
from streamlit_float import float_init, float_box

def main():
    float_init()
    st.title("Test Float Button")
    
    if float_box(
        '<div style="font-size: 16px;">Test Button</div>',
        width="120px",
        height="50px",
        right="20px",
        bottom="20px",
        background="#4CAF50",
        shadow=3
    ):
        st.write("Button clicked!")

if __name__ == "__main__":
    main()
