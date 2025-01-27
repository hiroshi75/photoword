import streamlit as st
from streamlit_float import float_init, float_box
import hashlib
from datetime import datetime
from models import SpanishVocabulary, ImageVocabularyResponse
from db import SessionLocal
from models_db import User, Image, VocabularyEntry
from sqlalchemy.orm import Session
from timeline import TimelineEntry, get_timeline_entries
from src.core.image_analysis import analyze_image, analyze_image_core, encode_image_data

from src.db.operations import get_or_create_user, save_image, save_vocabulary

def main():
    """
    Main function for the Photoword application.
    Provides a simple interface for uploading photos and analyzing them for Spanish vocabulary.
    """
    # Initialize floating functionality and session states
    float_init()
    
    st.title("Photoword - スペイン語単語帳")
    
    # Initialize all session states
    session_states = {
        "processed_image_hash": None,
        "show_modal": False,
        "current_image": None,
        "current_vocab": None,
        "search_term": "",
        "start_date": None,
        "end_date": None,
        "page_size": 5,
        "page_number": 1,
        "show_detail": None
    }
    
    # Initialize all states at once
    for key, default_value in session_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # Initialize database session
    db = SessionLocal()
    try:
        # Get or create test user
        user = get_or_create_user(db)
        
        # Add floating button using float_box with enhanced styling
        if float_box(
            '<div style="font-size: 16px; font-weight: 500;">画像を追加 ➕</div>',
            width="130px",
            height="50px",
            right="20px",
            bottom="20px",
            background="#4CAF50",
            shadow=4,
            transition=0.3,
            css="""
                cursor: pointer;
                color: white;
                text-align: center;
                padding: 12px;
                border-radius: 25px;
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
                &:hover {
                    background-color: #45a049 !important;
                    transform: translateY(-2px);
                }
            """
        ):
            st.session_state.show_modal = True
        
        # Import and use UI components
        from src.ui.components.modal import render_image_upload_modal
        from src.ui.components.filters import render_filters
        from src.ui.components.timeline import render_timeline
        
        # Render modal dialog
        render_image_upload_modal(db, user.id)
        
        # Get filter values
        search_term, start_date, end_date, page_size, skip = render_filters()
        
        # Get timeline entries with search
        timeline_entries = get_timeline_entries(
            db,
            user.id,
            skip=skip,
            limit=page_size,
            start_date=start_date,
            end_date=end_date,
            search_term=search_term
        )
        
        # Initialize detail view state if needed
        if "show_detail" not in st.session_state:
            st.session_state["show_detail"] = None
        
        # Render timeline
        render_timeline(timeline_entries)
        
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        main()
    finally:
        # Ensure database session is closed
        if 'db' in locals():
            db.close()
