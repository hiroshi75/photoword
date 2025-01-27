import streamlit as st
from datetime import datetime
from typing import Optional, Tuple

def render_filter_styles():
    """Render CSS styles for filter section."""
    st.markdown("""
        <style>
            .filter-section {
                background-color: #f8f9fa;
                padding: 1rem;
                border-radius: 10px;
                margin: 1rem 0;
            }
            [data-testid="stFileUploader"]:not([key="modal_uploader"]) {
                display: none !important;
            }
            [data-testid="stFileUploadDropzone"]:not([key="modal_uploader"]) {
                display: none !important;
            }
        </style>
        <div class="filter-section">
            <h3>🔍 フィルター</h3>
        </div>
    """, unsafe_allow_html=True)

def render_filters() -> Tuple[str, Optional[datetime], Optional[datetime], int, int]:
    """
    Render filter controls and return filter values.
    
    Returns:
        Tuple containing:
        - search_term: Text to search for
        - start_date: Start date filter
        - end_date: End date filter
        - page_size: Number of items per page
        - skip: Number of items to skip
    """
    render_filter_styles()
    
    filter_container = st.container()
    with filter_container:
        # Add search input
        st.text_input(
            "単語検索 (スペイン語または日本語)",
            placeholder="検索したい単語を入力...",
            key="search_term"
        )
        
        # Date range filters
        col1, col2 = st.columns(2)
        with col1:
            st.date_input(
                "開始日",
                key="start_date"
            )
        with col2:
            st.date_input(
                "終了日",
                key="end_date"
            )
    
    # Add pagination controls
    st.markdown("### 📄 ページ設定")
    pagination_container = st.container()
    with pagination_container:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.selectbox(
                "表示件数",
                options=[5, 10, 20],
                key="page_size"
            )
        with col2:
            st.number_input(
                "ページ番号",
                min_value=1,
                step=1,
                key="page_number"
            )
    
    skip = (st.session_state.page_number - 1) * st.session_state.page_size
    
    return (
        st.session_state.search_term if st.session_state.search_term else None,
        st.session_state.start_date if st.session_state.start_date else None,
        st.session_state.end_date if st.session_state.end_date else None,
        st.session_state.page_size,
        skip
    )
