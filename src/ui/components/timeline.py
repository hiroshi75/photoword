import streamlit as st
from typing import List
from timeline import TimelineEntry

def render_timeline_styles():
    """Render CSS styles for timeline display."""
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
