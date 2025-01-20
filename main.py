import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import HumanMessagePromptTemplate
import base64
import os

def encode_image_data(image_data):
    """
    Encode image data to base64.
    
    Args:
        image_data: Binary image data from uploaded file
        
    Returns:
        str: Base64 encoded image data
    """
    return base64.b64encode(image_data).decode('utf-8')

def analyze_image_with_llm(image_data):
    """
    Analyze image using Google's Gemini model via Langchain.
    
    Args:
        image_data: Binary image data from uploaded file
        
    Returns:
        list: A list of Spanish vocabulary words found in the image
    """
    base64_image = encode_image_data(image_data)
    image_template = {"image_url": {"url": f"data:image/png;base64,{base64_image}"}}
    
    chat = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-8b",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    
    system = "あなたは画像からスペイン語の単語を抽出する専門家です。画像に写っているものをスペイン語の単語として抽出してください。"
    human_prompt = "この画像からスペイン語の単語を抽出してください。"
    human_message_template = HumanMessagePromptTemplate.from_template([human_prompt, image_template])
    
    prompt = ChatPromptTemplate.from_messages([("system", system), human_message_template])
    chain = prompt | chat
    
    result = chain.invoke({})
    # TODO: Parse result to extract Spanish vocabulary words
    return ["manzana", "árbol", "coche"]  # Placeholder return until we implement proper parsing

def main():
    """
    Main function for the Photoword application.
    Provides a simple interface for uploading photos and analyzing them for Spanish vocabulary.
    """
    st.title("Photoword - スペイン語単語帳")
    st.subheader("写真をアップロードして単語帳を作成")
    
    # File uploader widget
    uploaded_file = st.file_uploader(
        "写真をアップロードしてください",
        type=["jpg", "jpeg", "png"],
        help="JPG、JPEG、またはPNG形式の画像ファイルをアップロードしてください。"
    )
    
    # Display uploaded image and analyze
    if uploaded_file is not None:
        st.image(uploaded_file, caption="アップロードされた画像")
        # Analyze image automatically upon upload
        vocab_list = analyze_image_with_llm(uploaded_file.getvalue())
        st.write("抽出された単語:", vocab_list)

if __name__ == "__main__":
    main()
