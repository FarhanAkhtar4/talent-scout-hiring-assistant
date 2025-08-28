import os
import json
import logging
from openai import OpenAI
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

logger = logging.getLogger(__name__)

class LLMHelper:
    def __init__(self):
        # Get API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
            self.client = None
        else:
            try:
                # Initialize OpenAI client without any additional parameters
                self.client = OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None
                
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    def extract_info(self, user_input: str) -> Dict[str, Any]:
        """Extract candidate information from user input"""
        if not self.client:
            return self._mock_extract_info(user_input)
            
        prompt = f"""
        Extract the following information from the candidate's message into JSON format:
        - name (string)
        - email (string)
        - phone (string)
        - years_experience (integer)
        - desired_position (string)
        - current_location (string)
        
        If any information is missing, set it to null.
        Return only valid JSON.
        
        Candidate's message: {user_input}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an information extraction assistant. Return only JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
        except Exception as e:
            logger.error(f"Error extracting info: {e}")
            return self._mock_extract_info(user_input)
    
    def _mock_extract_info(self, user_input: str) -> Dict[str, Any]:
        """Mock response for testing when OpenAI is not available"""
        # Simple pattern matching for demo purposes
        user_input_lower = user_input.lower()
        
        if "farhan" in user_input_lower:
            return {
                "name": "Farhan",
                "email": "farhan@example.com",
                "phone": "+1234567890",
                "years_experience": 5,
                "desired_position": "AI Developer",
                "current_location": "Bangalore, India"
            }
        elif "john" in user_input_lower:
            return {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+15551234567",
                "years_experience": 3,
                "desired_position": "Python Developer",
                "current_location": "New York, USA"
            }
        return {
            "name": None,
            "email": None,
            "phone": None,
            "years_experience": None,
            "desired_position": None,
            "current_location": None
        }
    
    def extract_tech_stack(self, user_input: str) -> List[str]:
        """Extract tech stack from user input"""
        if not self.client:
            return self._mock_extract_tech_stack(user_input)
            
        prompt = f"""
        Extract technologies, programming languages, frameworks, and tools from the candidate's message.
        Return only a JSON array of technologies.
        
        Candidate's message: {user_input}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a tech stack extraction assistant. Return only a JSON array."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
        except Exception as e:
            logger.error(f"Error extracting tech stack: {e}")
            return self._mock_extract_tech_stack(user_input)
    
    def _mock_extract_tech_stack(self, user_input: str) -> List[str]:
        """Mock tech stack extraction"""
        tech_keywords = ["python", "javascript", "java", "react", "node", "sql", "mongodb", "aws", 
                         "django", "flask", "vue", "angular", "docker", "kubernetes", "postgresql"]
        found_tech = []
        
        for tech in tech_keywords:
            if tech in user_input.lower():
                found_tech.append(tech.capitalize())
                
        return found_tech if found_tech else ["Python", "JavaScript", "React"]
    
    def generate_questions(self, tech_stack: List[str], years_experience: int) -> List[str]:
        """Generate technical questions based on tech stack"""
        if not self.client:
            return self._mock_generate_questions(tech_stack, years_experience)
            
        prompt = f"""
        Generate 3-5 technical questions appropriate for a candidate with {years_experience} years of experience.
        Focus on these technologies: {', '.join(tech_stack)}.
        Return only a JSON array of questions.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a technical interviewer. Return only a JSON array of questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return self._mock_generate_questions(tech_stack, years_experience)
    
    def _mock_generate_questions(self, tech_stack: List[str], years_experience: int) -> List[str]:
        """Mock question generation"""
        if not tech_stack:
            tech_stack = ["Python", "JavaScript"]
            
        return [
            f"What is your experience with {tech_stack[0]}?",
            f"Describe a challenging project you worked on using {tech_stack[0]}.",
            "How do you approach problem-solving in your work?",
            f"What development methodologies are you familiar with when working with {tech_stack[0]}?",
            "How do you stay updated with new technologies in your field?"
        ]