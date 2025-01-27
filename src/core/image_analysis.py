import json
import re
import base64
import hashlib
import os
import boto3
from typing import List
import streamlit as st
from models import SpanishVocabulary, ImageVocabularyResponse

# Initialize AWS Bedrock client
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1',
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
)

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
    Core function to analyze image using Claude Haiku via AWS Bedrock.
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
    
    prompt = """
上記の写真をスペイン語で表現したいというスペイン語学習者がいます。

あなたは上記の画像に写っている状況を説明するのに必要なスペイン語の単語や表現のリストを作ってあげてください。上記の写真に写っているものの名前などを、スペイン語・品詞・日本語・スペイン語例文の４つのデータのセットとして列挙してほしいです。

以下のようなデータ構成でリストを作ってください。(配列の中に、さらに４つの属性を持つデータとして作ってください。)
{
    "vocabulary": [{
        "word": "スペイン語の単語",
        "part_of_speech": "品詞（必ず「名詞」「動詞」「形容詞」「副詞」のなどを指定）",
        "translation": "日本語訳（必ず日本語で記載。例：「椅子」「テーブル」「窓」など）",
        "example_sentence": "その単語を使用したスペイン語の例文（必ず完全な文を記載）"
    }]
}

重要な注意点：
1. 各単語について、必ず4つの情報（word, part_of_speech, translation, example_sentence）を含めてください
2. translationは必ず日本語で記載してください（英語は使用しないでください）
3. 例文は必ず完全な文で記載してください
4. JSONの形式を厳密に守ってください
"""
    
    try:
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "temperature": 0,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": base64_image
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            })
        )
        
        response_body = json.loads(response.get('body').read())
        response_text = response_body['content'][0]['text']
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in response")
            
        json_str = json_match.group()
        data = json.loads(json_str)
        
        # Convert to SpanishVocabulary objects
        vocab_list = []
        for item in data.get("vocabulary", []):
            vocab = SpanishVocabulary(
                word=item["word"],
                part_of_speech=item["part_of_speech"],
                translation=item["translation"],
                example_sentence=item["example_sentence"]
            )
            vocab_list.append(vocab)
        
        return vocab_list
    except Exception as e:
        st.error(f"画像分析中にエラーが発生しました: {str(e)}")
        raise

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
