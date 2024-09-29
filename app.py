import streamlit as st
import os
from PyPDF2 import PdfReader
import docx
import tempfile
import requests

# Your Gemini API key
API_KEY = 'AIzaSyCr8niD4_LvntSAdd8apKnFC9uMZK5WeNU'  # Replace this with your actual API key

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "files" not in st.session_state:
    st.session_state.files = {}

def extract_text(file):
    """
    Extract text from PDF or DOCX files.
    """
    text = ""
    if file.name.endswith('.pdf'):
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    elif file.name.endswith('.docx'):
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text.strip()

def save_file(file):
    """
    Save uploaded files to a temporary directory.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp_file:
        tmp_file.write(file.getvalue())
        return tmp_file.name

def chat_with_gemini(prompt, context=""):
    """
    Send a prompt along with the context to the Gemini API and return the response.
    """
    try:
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": f"Context: {context}\n\nUser: {prompt}\n\nAssistant:"}
                    ]
                }
            ]
        }

        response = requests.post(endpoint, headers=headers, json=data)

        if response.status_code == 200:
            response_json = response.json()
            contents = response_json.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            if contents:
                return contents[0].get("text", "I couldn't generate a response. Please try again.")
            return "No relevant response text found in the API response."
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"An error occurred during API call: {str(e)}"

def main():
    st.set_page_config(page_title="Assignment Submission Chatbot", page_icon="📚", layout="wide")
    
    st.title("📚 Assignment Submission Chatbot")
    st.markdown("Welcome! Upload your assignments and let's chat about them.")

    with st.sidebar:
        st.header("📤 File Upload")
        uploaded_file = st.file_uploader("Choose a file (PDF or DOCX)", type=['pdf', 'docx'])
        if uploaded_file is not None:
            file_text = extract_text(uploaded_file)
            file_path = save_file(uploaded_file)
            st.session_state.files[uploaded_file.name] = {"path": file_path, "text": file_text}
            st.success(f"Great! I've uploaded '{uploaded_file.name}' for you.")

        st.header("📁 Your Files")
        for filename in st.session_state.files:
            st.write(f"- {filename}")

    st.header("💬 Let's Chat About Your Assignments")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me anything about your assignments..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        context = "\n\n".join([f"File: {filename}\nContent: {fileinfo['text'][:500]}..." for filename, fileinfo in st.session_state.files.items()])

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = chat_with_gemini(prompt, context)
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
