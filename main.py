import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import HumanMessagePromptTemplate
import base64
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

def encode_image_data(image_data):
    """
    Encode image data to base64.
    
    Args:
        image_data: Binary image data from uploaded file
        
    Returns:
        str: Base64 encoded image data
    """
    return base64.b64encode(image_data).decode('utf-8')

async def analyze_image_async(image_data):
    """
    Asynchronously analyze image using Google's Gemini model via Langchain.
    
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
        timeout=30,  # Add 30-second timeout to prevent blocking
        max_retries=2,
    )
    
    system = "あなたは画像に写っているものから、スペイン語学習者のための単語帳を作るために、可能な限り名詞、形容詞、副詞、その状況で使える動詞に変換してその単語を抽出する専門家です。画像に写っているものを全て説明するのに必要なスペイン語の単語一覧として抽出してください。"
    human_prompt = "この画像に写っているものからスペイン語の単語を可能な限り抽出してください。"
    human_message_template = HumanMessagePromptTemplate.from_template([human_prompt, image_template])
    
    prompt = ChatPromptTemplate.from_messages([("system", system), human_message_template])
    chain = prompt | chat
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, lambda: chain.invoke({}))
    # TODO: Parse result to extract Spanish vocabulary words
    return ["manzana", "árbol", "coche"]  # Placeholder return until we implement proper parsing

def analyze_image_with_timeout(image_data, timeout=30):
    """
    Wrapper function that runs the async analysis with a timeout.
    
    Args:
        image_data: Binary image data from uploaded file
        timeout: Maximum time to wait for analysis (seconds)
        
    Returns:
        list: A list of Spanish vocabulary words found in the image
    """
    try:
        return asyncio.run(asyncio.wait_for(analyze_image_async(image_data), timeout=timeout))
    except asyncio.TimeoutError:
        st.error("画像解析がタイムアウトしました。もう一度お試しください。")
        return []
    except Exception as e:
        st.error(f"画像解析中にエラーが発生しました: {str(e)}")
        return []

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
        st.image(uploaded_file)
        # Analyze image automatically upon upload
        vocab_list = analyze_image_with_timeout(uploaded_file.getvalue(), timeout=30)
        st.write("抽出された単語:", vocab_list)

if __name__ == "__main__":
    main()
