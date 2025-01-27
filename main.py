import streamlit as st
from streamlit_float import float_init, float_box
import hashlib
from datetime import datetime
from sqlalchemy.orm import Session

# Local imports
from models.models import SpanishVocabulary, ImageVocabularyResponse
from models_db import User, Image, VocabularyEntry
from db import SessionLocal
from db.operations import get_or_create_user, save_image, save_vocabulary

# Core functionality
from core.image_analysis import analyze_image, analyze_image_core, encode_image_data

# UI components
from ui.components.timeline import TimelineEntry, get_timeline_entries
from ui.components.modal import render_image_upload_modal
from ui.components.filters import render_filters
from ui.components.timeline import render_timeline
from ui.styles import load_styles

def main():
    """
    Main function for the Photoword application.
    Provides a simple interface for uploading photos and analyzing them for Spanish vocabulary.
    """
    st.set_page_config(layout="wide")  # Initialize page config first
    
    # Initialize floating functionality and styles
    float_init()
    load_styles()
    
    # Initialize all session states before any UI rendering
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.show_modal = False
        st.session_state.processed_image_hash = None
        st.session_state.current_image = None
        st.session_state.current_vocab = None
        st.session_state.search_term = ""
        st.session_state.start_date = None
        st.session_state.end_date = None
        st.session_state.page_size = 5
        st.session_state.page_number = 1
        st.session_state.show_detail = None
    
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
        elif key == "show_modal":  # Force modal to be hidden on page load
            st.session_state[key] = False
    
    # Initialize database session
    db = SessionLocal()
    try:
        # Get or create test user
        user = get_or_create_user(db)
        
        # Add floating button for image upload
        st.write(f"Before float_box: {st.session_state.show_modal}")  # Debug log
        if float_box(
            '<div style="color: white; border-radius: 25px; border: none; cursor: pointer;">画像を追加 ➕</div>',
            width="130px",
            height="50px",
            right="20px",
            bottom="20px",
            background="#4CAF50",
            shadow=4,
            transition=0.3
        ):
            st.session_state.show_modal = True
            st.rerun()
        st.write(f"After float_box: {st.session_state.show_modal}")  # Debug log
        
        # Use UI components
        
        # Render UI components
        render_image_upload_modal(db, user.id)
        search_term, start_date, end_date, page_size, skip = render_filters()
        
        # Get and render timeline entries
        timeline_entries = get_timeline_entries(
            db,
            user.id,
            skip=skip,
            limit=page_size,
            start_date=start_date,
            end_date=end_date,
            search_term=search_term
        )
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
