from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from models_db import User, Image, VocabularyEntry
from datetime import datetime

class TimelineEntry:
    """Data class representing a timeline entry."""
    def __init__(
        self,
        id: int,
        image_data: bytes,
        created_at: datetime,
        vocabulary_entries: List[VocabularyEntry]
    ):
        self.id = id
        self.image_data = image_data
        self.created_at = created_at
        self.vocabulary_entries = vocabulary_entries

def get_timeline_entries(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search_term: Optional[str] = None
) -> List[TimelineEntry]:
    """
    Retrieve timeline entries for a user with pagination, date filtering, and search functionality.
    
    Args:
        db: Database session
        user_id: User ID to fetch entries for
        skip: Number of entries to skip (for pagination)
        limit: Maximum number of entries to return
        start_date: Optional start date filter
        end_date: Optional end date filter
        search_term: Optional search term to filter vocabulary by Spanish or Japanese text
    
    Returns:
        List of TimelineEntry objects filtered by the given criteria
    """
    # Base query for images
    query = db.query(Image).filter(Image.user_id == user_id)
    
    # Apply search filter if provided
    if search_term:
        # Join with VocabularyEntry to search in vocabulary
        query = query.join(VocabularyEntry, VocabularyEntry.image_id == Image.id)
        query = query.filter(
            or_(
                VocabularyEntry.spanish_word.ilike(f"%{search_term}%"),
                VocabularyEntry.japanese_translation.ilike(f"%{search_term}%")
            )
        ).distinct()
    
    # Apply date filters if provided
    if start_date:
        # Ensure start_date is at the beginning of the day
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(Image.created_at >= start_date)
    if end_date:
        # Ensure end_date is at the end of the day
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        query = query.filter(Image.created_at <= end_date)
    
    # Order by creation date (newest first) and apply pagination
    images = query.order_by(desc(Image.created_at)).offset(skip).limit(limit).all()
    
    # Create timeline entries with associated vocabulary
    timeline_entries = []
    for image in images:
        vocab_entries = (
            db.query(VocabularyEntry)
            .filter(VocabularyEntry.image_id == image.id)
            .all()
        )
        
        entry = TimelineEntry(
            id=image.id,
            image_data=image.image_data,
            created_at=image.created_at,
            vocabulary_entries=vocab_entries
        )
        timeline_entries.append(entry)
    
    return timeline_entries
