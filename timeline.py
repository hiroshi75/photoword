from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
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
    end_date: Optional[datetime] = None
) -> List[TimelineEntry]:
    """
    Retrieve timeline entries for a user with pagination and date filtering.
    
    Args:
        db: Database session
        user_id: User ID to fetch entries for
        skip: Number of entries to skip (for pagination)
        limit: Maximum number of entries to return
        start_date: Optional start date filter
        end_date: Optional end date filter
    
    Returns:
        List of TimelineEntry objects
    """
    # Base query for images
    query = db.query(Image).filter(Image.user_id == user_id)
    
    # Apply date filters if provided
    if start_date:
        query = query.filter(Image.created_at >= start_date)
    if end_date:
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
