import google.generativeai as genai
from config import GEMINI_API_KEY, ASSESSMENT_MODEL_NAME

genai.configure(api_key=GEMINI_API_KEY)

class MentalHealthAssessor:
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name=ASSESSMENT_MODEL_NAME,
            generation_config={"temperature": 0.7, "max_output_tokens": 1000},
        )

    def assess_mental_health(self, conversation_history):
        assessment_prompt = f"""
        As a mental health professional, analyze the following conversation between a user and an AI counselor. 
        Provide a comprehensive assessment of the user's mental health based on their messages. 
        Consider factors such as mood, anxiety levels, stress, coping mechanisms, and any potential red flags.
        
        Conversation:
        {conversation_history}
        
        Please provide your assessment in the following format:
        1. Overall Mental Health Score (1-10):
        2. Key Observations:
        3. Potential Concerns:
        4. Recommendations:
        
        Respond with a structured assessment following the above format.
        """
        
        assessment_response = self.model.generate_content(assessment_prompt).text
        return assessment_response

