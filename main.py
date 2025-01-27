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
    
    # Add global styles
    st.markdown("""
        <style>
            /* Hide any legacy upload widgets while preserving modal uploader */
            [data-testid="stFileUploader"]:not([key="modal_uploader"]),
            [data-testid="stFileUploadDropzone"]:not([key="modal_uploader"]),
            .upload-container,
            .element-container:has(> [data-testid="stFileUploader"]:not([key="modal_uploader"])) {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize database session
    db = SessionLocal()
    try:
        # Get or create test user
        user = get_or_create_user(db)
        # Display timeline header with better styling
        st.markdown("""
            <style>
                .timeline-header {
                    margin-bottom: 2rem;
                    padding-bottom: 1rem;
                    border-bottom: 2px solid #f0f0f0;
                }
                .upload-container {
                    display: none !important;
                }
            </style>
            <div class="timeline-header">
                <h2>📸 タイムライン</h2>
            </div>
        """, unsafe_allow_html=True)
        
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
        
        # Modal dialog for image upload
        if st.session_state.show_modal:
            # Create a modal-like container with custom styling
            st.markdown("""
                <style>
                    .modal-overlay {
                        position: fixed;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background-color: rgba(0, 0, 0, 0.5);
                        z-index: 999999;
                    }
                    .modal-container {
                        background-color: white;
                        padding: 2rem;
                        border-radius: 10px;
                        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
                        margin: 2rem auto;
                        border: 1px solid #e0e0e0;
                        position: relative;
                        z-index: 1000000;
                        max-width: 800px;
                    }
                    .modal-header {
                        margin-bottom: 1.5rem;
                        padding-bottom: 1rem;
                        border-bottom: 2px solid #f0f0f0;
                    }
                    .modal-close {
                        position: absolute;
                        top: 1rem;
                        right: 1rem;
                        cursor: pointer;
                        font-size: 1.5rem;
                        color: #666;
                    }
                    .modal-close:hover {
                        color: #333;
                    }
                </style>
            """, unsafe_allow_html=True)
            
            # Add overlay
            st.markdown('<div class="modal-overlay"></div>', unsafe_allow_html=True)
            
            modal_container = st.container()
            with modal_container:
                with st.container():
                    st.markdown('<div class="modal-container" data-modal="true">', unsafe_allow_html=True)
                    st.markdown("""
                        <div class="modal-header">
                            <h3>画像のアップロード</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Add close button using Streamlit with custom styling
                    st.markdown("""
                        <style>
                            div[data-testid="stButton"] button:has(div:contains("×")) {
                                position: absolute;
                                top: 1rem;
                                right: 1rem;
                                padding: 0.5rem 1rem;
                                font-size: 1.5rem;
                                color: #666;
                                background: none;
                                border: none;
                                cursor: pointer;
                            }
                            div[data-testid="stButton"] button:has(div:contains("×")):hover {
                                color: #333;
                            }
                            /* Ensure file uploader is visible */
                            [data-testid="stFileUploader"] {
                                display: block !important;
                                margin: 1rem 0;
                                visibility: visible !important;
                                opacity: 1 !important;
                            }
                            [data-testid="stFileUploadDropzone"] {
                                display: block !important;
                                margin: 1rem 0;
                                visibility: visible !important;
                                opacity: 1 !important;
                            }
                            /* Hide legacy upload widgets */
                            [data-testid="stFileUploader"]:not([key="modal_uploader"]),
                            [data-testid="stFileUploadDropzone"]:not([key="modal_uploader"]) {
                                display: none !important;
                            }
                        </style>
                    """, unsafe_allow_html=True)
                    if st.button("×", key="modal_close_btn", help="モーダルを閉じる"):
                        st.session_state.show_modal = False
                        st.rerun()
                    
                    # File uploader in modal with improved styling and visibility
                    st.markdown("""
                        <style>
                        /* Modal styling */
                        div[data-modal="true"] {
                            position: fixed;
                            top: 50%;
                            left: 50%;
                            transform: translate(-50%, -50%);
                            z-index: 999999;
                            background: white;
                            padding: 20px;
                            border-radius: 5px;
                            box-shadow: 0 0 10px rgba(0,0,0,0.5);
                            width: 80%;
                            max-width: 800px;
                        }
                        
                        /* Ensure file uploader is visible and on top */
                        div[data-modal="true"] [data-testid="stFileUploader"] {
                            position: relative;
                            z-index: 1000000;
                            display: block !important;
                            visibility: visible !important;
                            opacity: 1 !important;
                            margin: 20px 0;
                        }
                        
                        /* Style the upload box */
                        div[data-modal="true"] [data-testid="stFileUploadDropzone"] {
                            border: 2px dashed #4CAF50;
                            border-radius: 5px;
                            padding: 20px;
                            text-align: center;
                            background: #f8f9fa;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    uploaded_file = st.file_uploader(
                        "写真をアップロードしてください",
                        type=["jpg", "jpeg", "png"],
                        key="modal_uploader",
                        help="JPG、JPEG、またはPNG形式の画像ファイルをアップロードしてください。"
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                
                if uploaded_file:
                    try:
                        # Read and verify image data
                        image_data = uploaded_file.getvalue()
                        current_hash = hashlib.md5(image_data).hexdigest()
                        
                        # Verify image data using PIL
                        from PIL import Image
                        import io
                        Image.open(io.BytesIO(image_data))
                        
                        # Create a new container for preview and analysis
                        with st.container():
                            st.markdown('<div class="modal-container">', unsafe_allow_html=True)
                            
                            # Show preview
                            st.image(image_data, use_container_width=True)
                    except Exception as e:
                        st.error(f"画像の読み込みに失敗しました: {str(e)}")
                        return
                        
                    # Analyze image with spinner
                    with st.spinner("画像を分析中..."):
                        vocab_list = analyze_image(image_data)
                    
                    if vocab_list:
                        st.markdown("### 📝 抽出された単語")
                        for vocab in vocab_list:
                            st.markdown(f"""
                            ### {vocab.word}
                            - 📚 [{vocab.part_of_speech}] {vocab.translation}
                            - 💭 {vocab.example_sentence}
                            ---
                            """)
                        
                        # Store current state
                        st.session_state.current_image = image_data
                        st.session_state.current_vocab = vocab_list
                        
                        # Add OK/Cancel buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("OK", key="modal_ok"):
                                if st.session_state.processed_image_hash != current_hash:
                                    # Save to database
                                    image = save_image(db, user.id, image_data)
                                    save_vocabulary(db, user.id, image.id, vocab_list)
                                    st.session_state.processed_image_hash = current_hash
                                    # Clear modal state
                                    st.session_state.show_modal = False
                                    st.session_state.current_image = None
                                    st.session_state.current_vocab = None
                                    st.rerun()
                                else:
                                    st.warning("この画像は既に処理済みです。")
                        with col2:
                            if st.button("キャンセル", key="modal_cancel"):
                                # Clear modal state
                                st.session_state.show_modal = False
                                st.session_state.current_image = None
                                st.session_state.current_vocab = None
                                st.rerun()
                    else:
                        st.error("単語を抽出できませんでした。別の画像を試してください。")
                        if st.button("閉じる", key="modal_close"):
                            st.session_state.show_modal = False
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
        
        # Get timeline entries
        
        # Add filter section with better styling
        st.markdown("""
            <style>
                .filter-section {
                    background-color: #f8f9fa;
                    padding: 1rem;
                    border-radius: 10px;
                    margin: 1rem 0;
                }
                /* Hide any legacy upload widgets */
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
        
        # Add pagination controls with better styling
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
        
        # Get timeline entries with search
        timeline_entries = get_timeline_entries(
            db,
            user.id,
            skip=skip,
            limit=st.session_state.page_size,
            start_date=st.session_state.start_date if st.session_state.start_date else None,
            end_date=st.session_state.end_date if st.session_state.end_date else None,
            search_term=st.session_state.search_term if st.session_state.search_term else None
        )
        
        # Initialize detail view state
        if "show_detail" not in st.session_state:
            st.session_state["show_detail"] = None

        # Display timeline entries with improved styling
        if timeline_entries:
            for entry in timeline_entries:
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
        else:
            st.info("表示するエントリーがありません。新しい画像をアップロードしてください。")
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
