import streamlit as st

def main():
    """
    Main function for the Photoword application.
    Provides a simple interface for uploading photos.
    """
    st.title("Photoword - スペイン語単語帳")
    st.subheader("写真をアップロードして単語帳を作成")
    
    # File uploader widget
    uploaded_file = st.file_uploader(
        "写真をアップロードしてください",
        type=["jpg", "jpeg", "png"],
        help="JPG、JPEG、またはPNG形式の画像ファイルをアップロードしてください。"
    )
    
    # Display uploaded file information
    if uploaded_file is not None:
        st.image(uploaded_file, caption="アップロードされた画像")
        st.write("ファイル名:", uploaded_file.name)
        st.write("ファイルサイズ:", f"{uploaded_file.size / 1024:.1f} KB")
        
        # Add button to trigger LLM analysis
        if st.button("画像解析を実行"):
            vocab_list = analyze_image_with_llm(uploaded_file)
            st.write("推定された単語リスト:", vocab_list)

def analyze_image_with_llm(uploaded_file):
    """
    Placeholder function for LLM-based image analysis.
    Will be replaced with actual Gemini integration in future updates.
    
    Args:
        uploaded_file: The uploaded image file from Streamlit
        
    Returns:
        list: A list of Spanish words found in the image
    """
    # TODO: Implement actual Gemini LLM integration
    return ["manzana", "árbol", "coche"]

if __name__ == "__main__":
    main()
