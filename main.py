import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import HumanMessagePromptTemplate
import base64
import os
from models import SpanishVocabulary, ImageVocabularyResponse

def encode_image_data(image_data):
    """
    Encode image data to base64.
    
    Args:
        image_data: Binary image data from uploaded file
        
    Returns:
        str: Base64 encoded image data
    """
    return base64.b64encode(image_data).decode('utf-8')

def analyze_image(image_data):
    """
    Analyze image using Google's Gemini model via Langchain.
    
    Args:
        image_data: Binary image data from uploaded file
        
    Returns:
        list: A list of Spanish vocabulary words found in the image
    """
    try:
        base64_image = encode_image_data(image_data)
        image_template = {"image_url": {"url": f"data:image/png;base64,{base64_image}"}}
        
        chat = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            max_tokens=None,
            timeout=30,  # 30-second timeout to prevent blocking
            max_retries=2,
        )
        
        system = """あなたは画像に写っているものから、スペイン語学習者のための単語帳を作るために、可能な限り名詞、形容詞、副詞、その状況で使える動詞に変換してその単語を抽出する専門家です。画像に写っているものを全て説明するのに必要なスペイン語の単語一覧として抽出してください。"""
        human_prompt = "この画像に写っているものからスペイン語の単語を可能な限り抽出してください。"
        human_message_template = HumanMessagePromptTemplate.from_template([human_prompt, image_template])
        
        prompt = ChatPromptTemplate.from_messages([("system", system), human_message_template])
        structured_chat = chat.with_structured_output(ImageVocabularyResponse)
        chain = prompt | structured_chat
        
        result = chain.invoke({})
        
        if not result or not result.vocabulary:
            st.warning("画像から単語を抽出できませんでした。別の画像を試してください。")
            return []
            
        return result.vocabulary  # Returns List[SpanishVocabulary]
    except ValueError as e:
        st.error("構造化データの解析に失敗しました。もう一度お試しください。")
        return []
    except TimeoutError as e:
        st.error("画像解析がタイムアウトしました。もう一度お試しください。")
        return []
    except Exception as e:
        st.error(f"予期せぬエラーが発生しました: {str(e)}")
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
        vocab_list = analyze_image(uploaded_file.getvalue())
        
        if vocab_list:
            st.subheader("抽出された単語:")
            for vocab_item in vocab_list:
                # Create a 3-row table for each vocabulary item
                data = [
                    [f"**{vocab_item.word}**"],  # 1行目: スペイン語の単語（太字で目立たせる）
                    [f"{vocab_item.part_of_speech}, {vocab_item.translation}"],  # 2行目: 品詞、日本語の意味
                    [vocab_item.example]  # 3行目: 例文
                ]
                st.table(data)
        else:
            st.write("単語を抽出できませんでした。")

if __name__ == "__main__":
    main()
