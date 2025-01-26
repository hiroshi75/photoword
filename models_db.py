from sqlalchemy import Column, Integer, String, ForeignKey, Text, CheckConstraint, LargeBinary
from sqlalchemy.sql import func
from sqlalchemy.types import TIMESTAMP
from db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    image_data = Column(LargeBinary)  # Using LargeBinary for image data
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

class VocabularyEntry(Base):
    __tablename__ = "vocabulary_entries"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    spanish_word = Column(String, nullable=False)
    part_of_speech = Column(String, nullable=False)
    japanese_translation = Column(String, nullable=False)
    example_sentence = Column(String, nullable=False)
    image_id = Column(Integer, ForeignKey("images.id"))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

class LearningProgress(Base):
    __tablename__ = "learning_progress"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    vocabulary_id = Column(Integer, ForeignKey("vocabulary_entries.id"))
    status = Column(String, CheckConstraint("status IN ('未学習','学習中','習得済み','要復習')"), nullable=False)
    last_reviewed = Column(TIMESTAMP, server_default=func.current_timestamp())
