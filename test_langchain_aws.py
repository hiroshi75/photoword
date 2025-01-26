import os
from langchain_aws import ChatBedrock

def test_chat_model():
    try:
        print("Testing langchain_aws import... ", end="")
        chat = ChatBedrock(
            model_id="anthropic.claude-3-haiku-20240307-v1:0",
            region_name="us-east-1",
            model_kwargs={"temperature": 0}
        )
        print("SUCCESS")
        print("Chat model initialized successfully")
        return True
    except Exception as e:
        print("FAILED")
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_chat_model()
