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

if __name__ == "__main__":
    main()
