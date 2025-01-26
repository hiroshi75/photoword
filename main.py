import streamlit as st
from langchain_aws import ChatBedrock
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
import base64
import os
from typing import List
from models import SpanishVocabulary, ImageVocabularyResponse
from db import SessionLocal
from models_db import User, Image, VocabularyEntry
from sqlalchemy.orm import Session

def encode_image_data(image_data):
    """
    Encode image data to base64.
    
    Args:
        image_data: Binary image data from uploaded file
        
    Returns:
        str: Base64 encoded image data
    """
    return base64.b64encode(image_data).decode('utf-8')

def analyze_image_core(image_data: bytes) -> List[SpanishVocabulary]:
    """
    Core function to analyze image using Google's Gemini model via Langchain.
    This function is independent of any UI framework.
    
    Args:
        image_data: Binary image data
        
    Returns:
        list[SpanishVocabulary]: A list of Spanish vocabulary words found in the image
        
    Raises:
        ValueError: If structured data parsing fails
        TimeoutError: If the request times out
        Exception: For any other unexpected errors
    """
    base64_image = encode_image_data(image_data)
    
    chat = ChatBedrock(
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        region_name="us-east-1",
        model_kwargs=dict(temperature=0)
    )
    
    human_template = """
上記の写真をスペイン語で表現したいというスペイン語学習者がいます。

あなたは上記の画像に写っている状況を説明するのに必要なスペイン語の単語や表現のリストを作ってあげてください。上記の写真に写っているものの名前などを、スペイン語・品詞・日本語・スペイン語例文の４つのデータのセットとして列挙してほしいです。

以下のようなデータ構成でリストを作ってください。(配列の中に、さらに４つの属性を持つデータとして作ってください。)
{
    vocabulary: [{
        word: スペイン語の単語
        part_of_speech: 品詞（必ず「名詞」「動詞」「形容詞」「副詞」のなどを指定）
        translation: 日本語訳
        example_sentence: その単語を使用したスペイン語の例文（必ず完全な文を記載）
    }, ...] //単語数分繰り返す
}

重要な注意点：
1. 各単語について、必ず4つの情報（word, part_of_speech, translation, example_sentence
2. 例文は必ず完全な文で記載してください
"""

    human_message = HumanMessage(content=[
        
        {
            "type": "image_url", 
            "image_url": {
                "url": f"data:image/png;base64,{base64_image}"
            }
        },
        {
            "type":"text",
            "text":human_template
        }
    ])
    prompt = ChatPromptTemplate.from_messages([
        human_message
    ])
    structured_chat = chat.with_structured_output(ImageVocabularyResponse)
    chain = prompt | structured_chat
    
    result = chain.invoke({})
    print(result)
    
    if not result or not result.vocabulary:
        return []
        
    return result.vocabulary  # Returns List[SpanishVocabulary]

def analyze_image(image_data: bytes) -> list[SpanishVocabulary]:
    """
    Analyze image using Google's Gemini model via Langchain.
    This function wraps analyze_image_core with Streamlit UI feedback.
    
    Args:
        image_data: Binary image data from uploaded file
        
    Returns:
        list[SpanishVocabulary]: A list of Spanish vocabulary words found in the image
    """
    try:
        vocab = analyze_image_core(image_data)
        if not vocab:
            st.warning("画像から単語を抽出できませんでした。別の画像を試してください。")
        return vocab
    except ValueError as e:
        st.error("構造化データの解析に失敗しました。もう一度お試しください。")
        return []
    except TimeoutError as e:
        st.error("画像解析がタイムアウトしました。もう一度お試しください。")
        return []
    except Exception as e:
        st.error(f"予期せぬエラーが発生しました: {str(e)}")
        return []

def get_or_create_user(db: Session, username: str = "test_user") -> User:
    """Get or create a test user for development."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        user = User(username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def save_image(db: Session, user_id: int, image_data: bytes) -> Image:
    """Save uploaded image to database."""
    try:
        image = Image(user_id=user_id, image_data=image_data)
        db.add(image)
        db.commit()
        db.refresh(image)
        return image
    except Exception as e:
        db.rollback()
        st.error(f"画像の保存中にエラーが発生しました: {str(e)}")
        raise

def save_vocabulary(db: Session, user_id: int, image_id: int, vocab_items: List[SpanishVocabulary]):
    """Save vocabulary entries to database."""
    try:
        for item in vocab_items:
            vocab_entry = VocabularyEntry(
                user_id=user_id,
                image_id=image_id,
                spanish_word=item.word,
                part_of_speech=item.part_of_speech,
                japanese_translation=item.translation,
                example_sentence=item.example_sentence
            )
            db.add(vocab_entry)
        db.commit()
    except Exception as e:
        db.rollback()
        st.error(f"単語の保存中にエラーが発生しました: {str(e)}")
        raise

def main():
    """
    Main function for the Photoword application.
    Provides a simple interface for uploading photos and analyzing them for Spanish vocabulary.
    """
    st.title("Photoword - スペイン語単語帳")
    st.subheader("写真をアップロードして単語帳を作成")
    
    # Initialize database session
    db = SessionLocal()
    try:
        # Get or create test user
        user = get_or_create_user(db)
        
        # File uploader widget
        uploaded_file = st.file_uploader(
            "写真をアップロードしてください",
            type=["jpg", "jpeg", "png"],
            help="JPG、JPEG、またはPNG形式の画像ファイルをアップロードしてください。"
        )
        
        # Display uploaded image and analyze
        if uploaded_file is not None:
            image_data = uploaded_file.getvalue()
            st.image(uploaded_file)
            vocab_list = analyze_image(image_data)
            
            if vocab_list:
                # Save image and vocabulary to database
                image = save_image(db, user.id, image_data)
                save_vocabulary(db, user.id, image.id, vocab_list)
                
                st.subheader("抽出された単語:")
                for vocab_item in vocab_list:
                    # Display vocabulary item in markdown format with bullet points
                    markdown_text = f"""
                    ### {vocab_item.word}
                    - [{vocab_item.part_of_speech}]{vocab_item.translation}
                    - {vocab_item.example_sentence}
                    """
                    st.markdown(markdown_text)
            else:
                st.write("単語を抽出できませんでした。")
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        main()
    finally:
        # Ensure database session is closed
        if 'db' in locals():
            db.close()
