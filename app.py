# app.py
import streamlit as st
import uuid
import json
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from models import CandidateInfo, TechStack
from llm_helper import LLMHelper
from storage import Storage

# Initialize helpers
llm = LLMHelper()
storage = Storage()

# Session state initialization
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "candidate_info" not in st.session_state:
        st.session_state.candidate_info = {}
    if "tech_stack" not in st.session_state:
        st.session_state.tech_stack = []
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0
    if "conversation_state" not in st.session_state:
        st.session_state.conversation_state = "greeting"  # greeting, collecting_info, collecting_tech, asking_questions, completed
    if "candidate_id" not in st.session_state:
        st.session_state.candidate_id = str(uuid.uuid4())[:8]

# Page configuration
st.set_page_config(
    page_title="TalentScout Hiring Assistant",
    page_icon="🤖",
    layout="centered"
)

# CSS for better styling
st.markdown("""
<style>
.chat-message {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
}
.chat-message.user {
    background-color: #f0f2f6;
}
.chat-message.assistant {
    background-color: #e6f7ff;
}
</style>
""", unsafe_allow_html=True)

def display_chat():
    """Display the chat conversation"""
    for message in st.session_state.messages:
        with st.container():
            st.markdown(f'<div class="chat-message {message["role"]}">', unsafe_allow_html=True)
            st.markdown(message["content"])
            st.markdown('</div>', unsafe_allow_html=True)

def add_message(role: str, content: str):
    """Add a message to the chat history"""
    st.session_state.messages.append({"role": role, "content": content})

def handle_user_input(user_input: str):
    """Handle user input based on current conversation state"""
    add_message("user", user_input)
    
    if st.session_state.conversation_state == "greeting":
        handle_info_collection(user_input)
    elif st.session_state.conversation_state == "collecting_info":
        handle_info_collection(user_input)
    elif st.session_state.conversation_state == "collecting_tech":
        handle_tech_stack(user_input)
    elif st.session_state.conversation_state == "asking_questions":
        handle_question_answer(user_input)

def handle_info_collection(user_input: str):
    """Handle candidate information collection"""
    extracted_info = llm.extract_info(user_input)
    
    # Update candidate info with extracted data
    st.session_state.candidate_info.update(extracted_info)
    
    # Check if we have all required information
    required_fields = ["name", "email", "phone", "years_experience", "desired_position", "current_location"]
    missing_fields = [field for field in required_fields if not st.session_state.candidate_info.get(field)]
    
    if missing_fields:
        # Ask for missing information
        if "name" in missing_fields:
            add_message("assistant", "Could you please provide your full name?")
        elif "email" in missing_fields:
            add_message("assistant", "What is your email address?")
        elif "phone" in missing_fields:
            add_message("assistant", "What is your phone number?")
        elif "years_experience" in missing_fields:
            add_message("assistant", "How many years of experience do you have?")
        elif "desired_position" in missing_fields:
            add_message("assistant", "What position are you applying for?")
        elif "current_location" in missing_fields:
            add_message("assistant", "Where are you currently located? (City, Country)")
    else:
        # All information collected, move to tech stack
        add_message("assistant", "Great! Now, could you tell me about your technical skills? What programming languages, frameworks, and tools are you proficient in?")
        st.session_state.conversation_state = "collecting_tech"

def handle_tech_stack(user_input: str):
    """Handle tech stack collection"""
    tech_stack = llm.extract_tech_stack(user_input)
    
    if tech_stack:
        st.session_state.tech_stack = tech_stack
        years_exp = st.session_state.candidate_info.get("years_experience", 0)
        
        # Generate questions based on tech stack
        questions = llm.generate_questions(tech_stack, years_exp)
        st.session_state.questions = questions
        st.session_state.current_question_index = 0
        
        # Ask the first question
        if questions:
            add_message("assistant", f"Thank you! Now I'll ask you a few technical questions. {questions[0]}")
            st.session_state.conversation_state = "asking_questions"
        else:
            add_message("assistant", "Thank you for the information! We'll review your details and get back to you soon.")
            st.session_state.conversation_state = "completed"
    else:
        add_message("assistant", "I didn't quite get that. Could you please list the technologies you work with? (e.g., Python, JavaScript, React)")

def handle_question_answer(user_input: str):
    """Handle question answering phase"""
    current_idx = st.session_state.current_question_index
    questions = st.session_state.questions
    
    if current_idx < len(questions) - 1:
        # Ask next question
        next_question = questions[current_idx + 1]
        add_message("assistant", next_question)
        st.session_state.current_question_index += 1
    else:
        # No more questions, end conversation
        add_message("assistant", "Thank you for completing the screening! We've collected all the necessary information. Our recruitment team will review your details and contact you shortly.")
        st.session_state.conversation_state = "completed"
        
        # Save candidate data
        candidate_data = {
            **st.session_state.candidate_info,
            "tech_stack": st.session_state.tech_stack,
            "questions": st.session_state.questions,
            "conversation": st.session_state.messages
        }
        storage.save_candidate(st.session_state.candidate_id, candidate_data)

def main():
    """Main application function"""
    init_session_state()
    
    st.title("TalentScout Hiring Assistant 🤖")
    st.caption("Your intelligent pre-screening partner")
    
    # Display chat messages
    display_chat()
    
    # Initial greeting
    if not st.session_state.messages:
        add_message("assistant", "Hello! Welcome to TalentScout. I'm here to assist with your initial screening. Could you please tell me a bit about yourself? Please include your name, email, phone number, years of experience, desired position, and current location.")
    
    # User input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        handle_user_input(user_input)
        st.rerun()
    
    # Sidebar with candidate info
    with st.sidebar:
        st.title("Candidate Info")
        if st.session_state.candidate_info:
            for key, value in st.session_state.candidate_info.items():
                if value:
                    st.write(f"{key.title()}: {value}")
        
        if st.session_state.tech_stack:
            st.write("Tech Stack:", ", ".join(st.session_state.tech_stack))
        
        if st.button("Reset Conversation"):
            st.session_state.messages = []
            st.session_state.candidate_info = {}
            st.session_state.tech_stack = []
            st.session_state.questions = []
            st.session_state.current_question_index = 0
            st.session_state.conversation_state = "greeting"
            st.session_state.candidate_id = str(uuid.uuid4())[:8]
            st.rerun()

if __name__ == "__main__":
    main()