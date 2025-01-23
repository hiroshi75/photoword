"""
Pydantic models for structured vocabulary data in the Photoword application.
"""
from typing import List
from pydantic import BaseModel, Field

class SpanishVocabulary(BaseModel):
    """スペイン語単語データのモデル"""
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
    example: str = Field(
        description="スペイン語の例文",
        min_length=1
    )

    class Config:
        """モデルの設定"""
        json_schema_extra = {
            "example": {
                "word": "manzana",
                "part_of_speech": "名詞",
                "translation": "りんご",
                "example": "La manzana está fresca."
            }
        }

class ImageVocabularyResponse(BaseModel):
    """画像から抽出された単語リストのレスポンスモデル"""
    vocabulary: List[SpanishVocabulary] = Field(
        description="抽出された単語リスト",
        min_items=1
    )

    class Config:
        """モデルの設定"""
        json_schema_extra = {
            "example": {
                "vocabulary": [
                    {
                        "word": "manzana",
                        "part_of_speech": "名詞",
                        "translation": "りんご",
                        "example": "La manzana está fresca."
                    },
                    {
                        "word": "comer",
                        "part_of_speech": "動詞",
                        "translation": "食べる",
                        "example": "Me gusta comer manzanas."
                    }
                ]
            }
        }
