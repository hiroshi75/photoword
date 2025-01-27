import streamlit as st
from typing import List
from models_db import Image, VocabularyEntry
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.ui.styles import load_styles

class TimelineEntry:
    """Class representing a timeline entry with image and vocabulary."""
    def __init__(self, id: int, created_at: datetime, image_data: bytes, vocabulary_entries: List[VocabularyEntry]):
        self.id = id
        self.created_at = created_at
        self.image_data = image_data
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
    Get timeline entries with filtering and pagination.
    
    Args:
        db: Database session
        user_id: User ID to get entries for
        skip: Number of entries to skip (for pagination)
        limit: Maximum number of entries to return
        start_date: Filter entries after this date
        end_date: Filter entries before this date
        search_term: Search term to filter vocabulary
        
    Returns:
        List of TimelineEntry objects
    """
    # Start with base query for images
    query = db.query(Image).filter(Image.user_id == user_id)
    
    # Apply date filters if provided
    if start_date:
        query = query.filter(Image.created_at >= start_date)
    if end_date:
        query = query.filter(Image.created_at <= end_date)
    
    # Order by creation date (newest first) and apply pagination
    query = query.order_by(desc(Image.created_at)).offset(skip).limit(limit)
    
    # Execute query and build timeline entries
    timeline_entries = []
    for image in query.all():
        # Get vocabulary entries for this image
        vocab_query = db.query(VocabularyEntry).filter(
            VocabularyEntry.image_id == image.id
        )
        
        # Apply search term filter if provided
        if search_term:
            vocab_query = vocab_query.filter(
                (VocabularyEntry.spanish_word.ilike(f"%{search_term}%")) |
                (VocabularyEntry.japanese_translation.ilike(f"%{search_term}%"))
            )
        
        # Only include images that have matching vocabulary after search
        vocab_entries = vocab_query.all()
        if not search_term or vocab_entries:
            timeline_entries.append(TimelineEntry(
                id=image.id,
                created_at=image.created_at,
                image_data=image.image_data,
                vocabulary_entries=vocab_entries
            ))
    
    return timeline_entries

def render_timeline_styles():
    """Render CSS styles for timeline display."""
    load_styles()
    st.markdown("""
        <div class="timeline-header">
            <h2>📸 タイムライン</h2>
        </div>
    """, unsafe_allow_html=True)

def render_timeline(entries: List[TimelineEntry]) -> None:
    """
    Render timeline entries with images and vocabulary.
    
    Args:
        entries: List of TimelineEntry objects to display
    """
    render_timeline_styles()
    
    if not entries:
        st.info("表示するエントリーがありません。新しい画像をアップロードしてください。")
        return
    
    for entry in entries:
        with st.expander(
            f"📸 {entry.created_at.strftime('%Y年%m月%d日 %H:%M')}",
            expanded=True
        ):
            # Create columns for image, vocabulary, and detail button
            img_col, vocab_col, btn_col = st.columns([2, 3, 1])
            
            # Display image in left column
            with img_col:
                st.image(entry.image_data, use_container_width=True)
            
            # Display vocabulary items in middle column
            with vocab_col:
                for vocab in entry.vocabulary_entries:
                    markdown_text = f"""
                    ### {vocab.spanish_word}
                    - 📚 [{vocab.part_of_speech}] {vocab.japanese_translation}
                    - 💭 {vocab.example_sentence}
                    ---
                    """
                    st.markdown(markdown_text)
            
            # Add detail view button in right column
            with btn_col:
                if st.button("詳細を表示", key=f"detail_btn_{entry.id}"):
                    st.session_state["show_detail"] = entry.id
        
        # Show detail modal if this entry is selected
        if st.session_state["show_detail"] == entry.id:
            with st.container():
                st.markdown("---")
                st.markdown("## 📝 詳細表示")
                
                # Display full-size image
                st.image(entry.image_data, use_container_width=True)
                
                # Display comprehensive vocabulary information
                st.markdown("### 📚 単語リスト")
                for vocab in entry.vocabulary_entries:
                    st.markdown(f"""
                    #### {vocab.spanish_word}
                    - **品詞**: {vocab.part_of_speech}
                    - **日本語**: {vocab.japanese_translation}
                    - **例文**: {vocab.example_sentence}
                    """)
                
                # Add close button
                if st.button("閉じる", key=f"close_btn_{entry.id}"):
                    st.session_state["show_detail"] = None
                st.markdown("---")
