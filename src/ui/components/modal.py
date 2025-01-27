import streamlit as st
from typing import Optional, Tuple
import hashlib
import io
from PIL import Image
from core.image_analysis import analyze_image
from db.operations import save_image, save_vocabulary
from ui.styles import load_styles

def render_modal_styles():
    """Render CSS styles for modal dialog."""
    load_styles()

def render_image_upload_modal(db, user_id: int) -> None:
    """Render the image upload modal dialog."""
    st.write(f"Modal state: {st.session_state.show_modal}")  # Debug log
    
    if not st.session_state.show_modal:
        return

    render_modal_styles()
    st.markdown("""
        <style>
        .modal-overlay { display: block !important; }
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
