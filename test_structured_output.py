import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from models import SpanishVocabulary, ImageVocabularyResponse

def test_structured_output():
    """構造化出力のテスト関数"""
    parser = JsonOutputParser(pydantic_object=ImageVocabularyResponse)
    
    chat = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-8b",
        temperature=0,
        max_tokens=None,
        timeout=30
    )

    system = """あなたは画像に写っているものから、スペイン語学習者のための単語帳を作成する専門家です。
以下の形式でJSONレスポンスを返してください:

{
    "vocabulary": [
        {
            "word": "スペイン語の単語",
            "part_of_speech": "品詞",
            "translation": "日本語訳",
            "example": "スペイン語の例文"
        }
    ]
}

各フィールドの説明:
- word: スペイン語の単語
- part_of_speech: 品詞（名詞、動詞、形容詞、副詞など）
- translation: 日本語訳
- example: その単語を使用したスペイン語の例文

画像に写っているものを全て説明するのに必要なスペイン語の単語を抽出し、上記の形式で返してください。"""

    human = "この画像から単語を抽出し、指定された形式で返してください。"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", human)
    ])
    
    chain = prompt | chat | parser
    
    # Test with dummy response for now
    dummy_response = {
        "vocabulary": [
            {
                "word": "manzana",
                "part_of_speech": "名詞",
                "translation": "りんご",
                "example": "La manzana está fresca."
            }
        ]
    }
    
    print("Test response structure:", dummy_response)
    print("Pydantic model validation:", ImageVocabularyResponse(**dummy_response))

if __name__ == "__main__":
    test_structured_output()
