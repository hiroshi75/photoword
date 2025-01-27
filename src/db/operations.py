from sqlalchemy.orm import Session
import streamlit as st
from models_db import User, Image, VocabularyEntry
from typing import List
from models import SpanishVocabulary

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
