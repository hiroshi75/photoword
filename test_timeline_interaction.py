import pytest
from datetime import datetime, timedelta
import base64
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import Base
from models_db import User, Image, VocabularyEntry
from src.db.operations import get_or_create_user, save_image, save_vocabulary
from timeline import get_timeline_entries

# Test database setup
TEST_DATABASE_URL = "sqlite:///test_photoword.db"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

@pytest.fixture
def test_db():
    """Create test database and tables."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(test_db):
    """Create a test user."""
    user = User(username="test_user")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def test_data(test_db, test_user):
    """Create test timeline entries with vocabulary."""
    # Create test image data
    with open('test_image/test1_restaurant.jpg', 'rb') as f:
        image_data = f.read()
    
    # Create two test images
    images = []
    for i in range(2):
        image = Image(
            user_id=test_user.id,
            image_data=image_data,
            created_at=datetime.now() - timedelta(days=i)
        )
        test_db.add(image)
        test_db.commit()
        test_db.refresh(image)
        images.append(image)
    
    # Create test vocabulary entries
    vocab_data = [
        {
            "spanish_word": "restaurante",
            "part_of_speech": "nombre",
            "japanese_translation": "レストラン",
            "example_sentence": "Este restaurante tiene una vista impresionante."
        },
        {
            "spanish_word": "mesa",
            "part_of_speech": "nombre",
            "japanese_translation": "テーブル",
            "example_sentence": "Hay una mesa junto a la ventana."
        },
        {
            "spanish_word": "silla",
            "part_of_speech": "nombre",
            "japanese_translation": "椅子",
            "example_sentence": "La silla es muy cómoda."
        }
    ]
    
    for image in images:
        for data in vocab_data:
            vocab = VocabularyEntry(
                user_id=test_user.id,
                image_id=image.id,
                **data
            )
            test_db.add(vocab)
    
    test_db.commit()
    return images, vocab_data

def test_search_functionality(test_db, test_user, test_data):
    """Test search functionality in timeline entries."""
    images, _ = test_data
    
    # Test Spanish word search
    entries = get_timeline_entries(
        test_db,
        test_user.id,
        search_term="restaurante"
    )
    assert len(entries) == 2
    for entry in entries:
        assert any(v.spanish_word == "restaurante" for v in entry.vocabulary_entries)
    
    # Test Japanese translation search
    entries = get_timeline_entries(
        test_db,
        test_user.id,
        search_term="テーブル"
    )
    assert len(entries) == 2
    for entry in entries:
        assert any(v.japanese_translation == "テーブル" for v in entry.vocabulary_entries)
    
    # Test partial match search
    entries = get_timeline_entries(
        test_db,
        test_user.id,
        search_term="rest"
    )
    assert len(entries) == 2
    for entry in entries:
        assert any("rest" in v.spanish_word.lower() for v in entry.vocabulary_entries)

def test_pagination_and_date_filtering(test_db, test_user, test_data):
    """Test pagination and date filtering in timeline entries."""
    images, _ = test_data
    
    # Test pagination
    entries = get_timeline_entries(
        test_db,
        test_user.id,
        skip=1,
        limit=1
    )
    assert len(entries) == 1
    assert entries[0].id == images[1].id
    
    # Test date filtering
    yesterday = datetime.now() - timedelta(days=1)
    tomorrow = datetime.now() + timedelta(days=1)
    
    # Test start_date filter
    entries = get_timeline_entries(
        test_db,
        test_user.id,
        start_date=yesterday
    )
    assert len(entries) == 2
    
    # Test end_date filter
    entries = get_timeline_entries(
        test_db,
        test_user.id,
        end_date=tomorrow
    )
    assert len(entries) == 2
    
    # Test date range
    entries = get_timeline_entries(
        test_db,
        test_user.id,
        start_date=yesterday,
        end_date=tomorrow
    )
    assert len(entries) == 2

def test_combined_filters(test_db, test_user, test_data):
    """Test combination of search, pagination, and date filtering."""
    images, _ = test_data
    
    # Test search with pagination
    entries = get_timeline_entries(
        test_db,
        test_user.id,
        search_term="mesa",
        skip=1,
        limit=1
    )
    assert len(entries) == 1
    assert any(v.spanish_word == "mesa" for v in entries[0].vocabulary_entries)
    
    # Test search with date filter
    yesterday = datetime.now() - timedelta(days=1)
    entries = get_timeline_entries(
        test_db,
        test_user.id,
        search_term="silla",
        start_date=yesterday
    )
    assert len(entries) == 2
    for entry in entries:
        assert any(v.spanish_word == "silla" for v in entry.vocabulary_entries)
