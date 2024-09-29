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

def chat_with_gemini(prompt, context=""):
    try:
        # Prepare the request to the Gemini API
        endpoint = f"https://generativelanguage.googleapis.com/v1beta2/models/gemini-1.5-flash:generateMessage?key={API_KEY}"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "messages": [
                {"author": "system", "content": "You are a helpful assistant."},
                {"author": "user", "content": f"{context}\n\n{prompt}"}
            ]
        }

        # Call the Gemini API
        response = requests.post(endpoint, headers=headers, json=data)

        # Check for a successful response
        if response.status_code == 200:
            # Extract the text in a readable format
            response_json = response.json()
            messages = response_json.get("candidates", [])
            if messages:
                # Extract only relevant text and format it
                text = messages[0].get("content", "No response text found.")
                return format_response(text)
            return "No relevant response text found."
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"An error occurred during API call: {str(e)}"

def format_response(text):
    """
    Format the API response text to be human-readable.
    """
    # Split text into sentences for better readability and structure the response
    sentences = text.split('. ')
    formatted_text = ""
    
    # Clean and structure the response by filtering out irrelevant parts
    for sentence in sentences:
        cleaned_sentence = sentence.strip()
        if len(cleaned_sentence) > 0:  # Only keep non-empty sentences
            formatted_text += f"- {cleaned_sentence}.\n\n"  # Bullet-point format for better readability
    
    return formatted_text

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
