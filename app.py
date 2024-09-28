import streamlit as st
import os
from PyPDF2 import PdfReader
import docx
import tempfile
import requests
from google.oauth2 import service_account

# Path to your service account key file
SERVICE_ACCOUNT_FILE = 'service_account.json'  # Adjust the path to match your folder structure

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "files" not in st.session_state:
    st.session_state.files = {}

def extract_text(file):
    text = ""
    if file.name.endswith('.pdf'):
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""  # Handle None if extraction fails
    elif file.name.endswith('.docx'):
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text.strip()  # Remove any extra whitespace

def save_file(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp_file:
        tmp_file.write(file.getvalue())
        return tmp_file.name

def get_access_token():
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        access_token_info = credentials.refresh(requests.Request())
        return access_token_info.token
    except Exception as e:
        st.error(f"Failed to obtain access token: {str(e)}")
        return None

def chat_with_gemini(prompt, context=""):
    access_token = get_access_token()  # Get the OAuth 2.0 access token
    if not access_token:
        return "Failed to get access token."

    try:
        # Prepare the request to the Gemini API
        endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"  # Replace with your endpoint
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": f"{context}\n\n{prompt}",
            "max_tokens": 150,  # Adjust as necessary
            "temperature": 0.7,  # Adjust temperature for response variability
        }

        # Call the Gemini API
        response = requests.post(endpoint, headers=headers, json=data)

        # Check for a successful response
        if response.status_code == 200:
            return response.json().get("choices", [{}])[0].get("text", "No response text found.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"An error occurred during API call: {str(e)}"

def main():
    st.set_page_config(page_title="Assignment Submission Chatbot", page_icon="📚", layout="wide")
    
    st.title("📚 Assignment Submission Chatbot")
    st.markdown("Welcome to the Assignment Submission Chatbot! Upload your assignments and chat about them.")

    # Sidebar for file upload
    with st.sidebar:
        st.header("📤 File Upload")
        uploaded_file = st.file_uploader("Choose a file (PDF or DOCX)", type=['pdf', 'docx'])
        if uploaded_file is not None:
            file_text = extract_text(uploaded_file)
            file_path = save_file(uploaded_file)
            st.session_state.files[uploaded_file.name] = {"path": file_path, "text": file_text}
            st.success(f"File uploaded: {uploaded_file.name}")

        st.header("📁 Uploaded Files")
        for filename in st.session_state.files:
            st.write(filename)

    # Main chat interface
    st.header("💬 Chat")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about your assignments..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare context from uploaded files
        context = "\n\n".join([f"File: {filename}\nContent: {fileinfo['text'][:500]}..." for filename, fileinfo in st.session_state.files.items()])

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = chat_with_gemini(prompt, context)
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
