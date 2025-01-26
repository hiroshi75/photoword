import os
import pytest
from main import analyze_image_core
from models import SpanishVocabulary

def test_analyze_image_core_restaurant():
    """Test analyze_image_core with restaurant test image"""
    # Read test image
    with open("test_image/test1_restaurant.jpg", "rb") as f:
        image_data = f.read()
    
    # Get vocabulary from image
    print("start")
    result = analyze_image_core(image_data)
    print(result)
    
    # Basic validation
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(item, SpanishVocabulary) for item in result)
    
    # Check that we got at least one expected word
    # Note: Translation might vary, so we check Japanese translations
    expected_words = ["椅子", "テーブル", "窓", "床", "レストラン", "ホール", "ライト"]
    translations = [item.translation for item in result]
    
    # At least one expected word should be found
    assert any(
        any(expected in trans for expected in expected_words)
        for trans in translations
    ), f"None of the expected words {expected_words} found in translations {translations}"
