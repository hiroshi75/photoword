from typing import List
from sqlalchemy.orm import Session
from models_db import User, Image, VocabularyEntry
from models.models import SpanishVocabulary
from db import SessionLocal

def get_or_create_user(db: Session, username: str = "test_user") -> User:
    """Get existing user or create a new one."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        user = User(username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def save_image(db: Session, user_id: int, image_data: bytes) -> Image:
    """Save uploaded image to database."""
    image = Image(user_id=user_id, image_data=image_data)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image

def save_vocabulary(db: Session, user_id: int, image_id: int, vocabulary_list: List[SpanishVocabulary]) -> List[VocabularyEntry]:
    """Save vocabulary entries to database."""
    entries = []
    for vocab in vocabulary_list:
        entry = VocabularyEntry(
            user_id=user_id,
            image_id=image_id,
            spanish_word=vocab.word,
            part_of_speech=vocab.part_of_speech,
            japanese_translation=vocab.translation,
            example_sentence=vocab.example_sentence
        )
        db.add(entry)
        entries.append(entry)
    
    db.commit()
    for entry in entries:
        db.refresh(entry)
    return entries
