import streamlit as st
from typing import Optional, Tuple
import hashlib
from src.core.image_analysis import analyze_image
from src.db.operations import save_image, save_vocabulary

def render_modal_styles():
    """Render CSS styles for modal dialog."""
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
            div[data-modal="true"] [data-testid="stFileUploader"] {
                position: relative;
                z-index: 1000000;
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
                margin: 20px 0;
            }
            div[data-modal="true"] [data-testid="stFileUploadDropzone"] {
                border: 2px dashed #4CAF50;
                border-radius: 5px;
                padding: 20px;
                text-align: center;
                background: #f8f9fa;
            }
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
            [data-testid="stFileUploader"]:not([key="modal_uploader"]),
            [data-testid="stFileUploadDropzone"]:not([key="modal_uploader"]) {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)

def render_image_upload_modal(db, user_id: int) -> None:
    """Render the image upload modal dialog."""
    if not st.session_state.show_modal:
        return

    render_modal_styles()
    
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
            
            if st.button("×", key="modal_close_btn", help="モーダルを閉じる"):
                st.session_state.show_modal = False
                st.rerun()
            
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
                            image = save_image(db, user_id, image_data)
                            save_vocabulary(db, user_id, image.id, vocab_list)
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
