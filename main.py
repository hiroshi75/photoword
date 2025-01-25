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

def analyze_image_core(image_data: bytes) -> list[SpanishVocabulary]:
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
    image_template = {"image_url": {"url": f"data:image/png;base64,{base64_image}"}}
    
    chat = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0,
        max_tokens=None,
        timeout=30,  # 30-second timeout to prevent blocking
        max_retries=2,
    )
    
    system = """あなたは画像に写っているものから、スペイン語学習者のための単語帳を作成する専門家です。
画像に写っているものを説明するのに必要なスペイン語の単語を抽出してください。

以下の形式で単語リストを返してください：

{
  "vocabulary": [
    {
      "word": "silla",
      "part_of_speech": "名詞",
      "translation": "椅子",
      "example": "Hay una silla junto a la mesa."
    }
  ]
}

各単語について、以下の4つの情報を必ず漏れなく含めてください：
1. word: スペイン語の単語（例：mesa, silla, ventana）
2. part_of_speech: 品詞（必ず「名詞」「動詞」「形容詞」「副詞」のいずれかを指定）
3. translation: 日本語訳（例：テーブル、椅子、窓）
4. example: その単語を使用したスペイン語の例文（必ず完全な文を記載）

特に注目すべき要素：
- 椅子 (silla)
- テーブル (mesa)
- 窓 (ventana)
- 床 (suelo)
- レストラン (restaurante)
- ホール (sala)
- ライト (luz)

重要な注意点：
1. 各単語について、必ず4つの情報（word, part_of_speech, translation, example）を全て含めてください
2. 品詞は必ず「名詞」「動詞」「形容詞」「副詞」のいずれかを指定してください
3. 例文は必ず完全な文で記載してください
4. 1つの情報でも欠けている場合はエラーとなりますので、全ての情報を必ず含めてください"""

    human_template = """この画像から単語を抽出し、各単語について以下の4つの情報を必ず漏れなく含めてください。
1つでも欠けている場合はエラーとなります：

1. word (必須): スペイン語の単語
2. part_of_speech (必須): 品詞（名詞、動詞、形容詞、副詞のいずれか）
3. translation (必須): 日本語訳
4. example (必須): スペイン語の例文（完全な文）

画像: {image_url}"""

    human_message = HumanMessagePromptTemplate.from_template(human_template)
    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        human_message
    ])
    structured_chat = chat.with_structured_output(ImageVocabularyResponse)
    chain = prompt | structured_chat
    
    result = chain.invoke({"image_url": image_template["image_url"]["url"]})
    
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
