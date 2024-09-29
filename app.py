import streamlit as st
import os
from PyPDF2 import PdfReader
import docx
import tempfile
import requests
import json

# Your Gemini API key
API_KEY = 'AIzaSyCr8niD4_LvntSAdd8apKnFC9uMZK5WeNU'  # Replace with your actual API key

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = {}
if "files" not in st.session_state:
    st.session_state.files = {}
if "current_course" not in st.session_state:
    st.session_state.current_course = None

# Mock course data
COURSES = {
    "Business Consulting - DIV B": {
        "assignments": [
            {
                "name": "Revised Business proposal and Defence",
                "due_date": "2024-09-18 11:55 PM",
                "status": "Not submitted",
                "requirements": "Submit a 10-page business proposal and prepare a 15-minute defense presentation."
            }
        ]
    },
    "Negotiation Skills - DIV B": {
        "assignments": [
            {
                "name": "Case Study Analysis",
                "due_date": "2024-10-01 11:59 PM",
                "status": "Not started",
                "requirements": "Analyze the provided case study and submit a 5-page report on negotiation strategies."
            }
        ]
    }
}

def extract_text(file):
    # (Keep the existing extract_text function)
    ...

def save_file(file):
    # (Keep the existing save_file function)
    ...

def chat_with_gemini(prompt, context=""):
    # (Keep the existing chat_with_gemini function)
    ...

def main():
    st.set_page_config(page_title="ekosh Assignment Assistant", page_icon="📚", layout="wide")
    
    # Custom CSS to match Moodle ekosh style with pastel colors
    st.markdown("""
    <style>
    .stApp {
        background-color: #f0f0f0;
    }
    .stSidebar {
        background-color: #e6d0e8;
    }
    .stButton>button {
        background-color: #d4b6d8;
        color: #4a0e4e;
    }
    .stChat > div {
        background-color: #f9f0fa;
    }
    </style>
    """, unsafe_allow_html=True)

    # Top navigation bar
    st.markdown("""
    <div style="background-color: #d4b6d8; padding: 10px; display: flex; justify-content: space-between; align-items: center;">
        <span style="color: #4a0e4e; font-size: 24px;">📚 ekosh Assignment Assistant</span>
        <span style="color: #4a0e4e;">Rudresh Dahiya</span>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar for course selection
    with st.sidebar:
        st.header("📁 Your Courses")
        for course in COURSES.keys():
            if st.button(course):
                st.session_state.current_course = course
                if course not in st.session_state.messages:
                    st.session_state.messages[course] = []
                st.experimental_rerun()

    # Main content area
    if st.session_state.current_course:
        st.subheader(f"💬 {st.session_state.current_course} Assistant")
        
        # Display assignments for the current course
        course_data = COURSES[st.session_state.current_course]
        for assignment in course_data["assignments"]:
            st.markdown(f"""
            <div style="background-color: #f9f0fa; padding: 10px; margin: 10px 0; border-radius: 5px; border: 1px solid #d4b6d8;">
                <h3>{assignment['name']}</h3>
                <p>Due: {assignment['due_date']}</p>
                <p>Status: {assignment['status']}</p>
                <p>Requirements: {assignment['requirements']}</p>
            </div>
            """, unsafe_allow_html=True)

        # Chat interface
        for message in st.session_state.messages[st.session_state.current_course]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask me about your assignments..."):
            st.session_state.messages[st.session_state.current_course].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = chat_with_gemini(prompt, context=json.dumps(course_data))
                message_placeholder.markdown(full_response)
            st.session_state.messages[st.session_state.current_course].append({"role": "assistant", "content": full_response})
    else:
        st.info("Please select a course from the sidebar to begin.")

if __name__ == "__main__":
    main()
