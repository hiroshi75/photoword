"""
Pydantic models for structured vocabulary data in the Photoword application.
"""
from typing import List
from pydantic import BaseModel, Field

class SpanishVocabulary(BaseModel):
    """抽出されたスペイン語の単語の情報"""
    word: str = Field(
        description="スペイン語の単語",
        min_length=1
    )
    part_of_speech: str = Field(
        description="品詞 (名詞、動詞、形容詞、副詞など)",
        min_length=1
    )
    translation: str = Field(
        description="日本語訳",
        min_length=1
    )
    example_sentence: str = Field(
        description="スペイン語の例文",
        min_length=1
    )

class ImageVocabularyResponse(BaseModel):
    """画像から抽出された単語リスト"""
    vocabulary: List[SpanishVocabulary] = Field(
        description="抽出されたSpanishVocabularyのリスト",
        min_length=1
    )
