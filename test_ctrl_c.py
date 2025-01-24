import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import HumanMessagePromptTemplate
import base64

def simulate_llm_call(image_data):
    """
    Simulate actual LLM call with same configuration as main app.
    """
    base64_image = base64.b64encode(image_data).decode('utf-8')
    image_template = {"image_url": {"url": f"data:image/png;base64,{base64_image}"}}
    
    chat = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-8b",
        temperature=0,
        max_tokens=None,
        timeout=30,  # Add 30-second timeout to prevent blocking
        max_retries=2,
    )
    
    system = "Test prompt"
    human_prompt = "Analyze this image"
    human_message_template = HumanMessagePromptTemplate.from_template([human_prompt, image_template])
    
    prompt = ChatPromptTemplate.from_messages([("system", system), human_message_template])
    chain = prompt | chat
    
    result = chain.invoke({})
    return ["test1", "test2", "test3"]  # Still return dummy data for consistency

def main():
    """
    Minimal test app to reproduce CTRL+C handling issues.
    """
    st.title("CTRL+C Test App")
    
    # File uploader widget (same as main app)
    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["jpg", "jpeg", "png"]
    )
    
    # Process file on upload
    if uploaded_file is not None:
        st.image(uploaded_file)
        with st.spinner("Processing..."):
            result = simulate_llm_call(uploaded_file.getvalue())
            st.write("Results:", result)

if __name__ == "__main__":
    main()
