import google.generativeai as genai
from config import GEMINI_API_KEY, CHATBOT_MODEL_NAME

genai.configure(api_key=GEMINI_API_KEY)

class Chatbot:
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name=CHATBOT_MODEL_NAME,
            generation_config={"temperature": 1, "max_output_tokens": 8192},
        )
        self.chat_session = self.model.start_chat(history=[])
        self._add_system_message()

    def _add_system_message(self):
        system_message = "You are an empathetic and supportive mental health chatbot. Provide helpful and compassionate responses to users seeking mental health support. Remember to encourage professional help when necessary."
        self.chat_session.send_message(system_message)

    def get_response(self, user_input):
        return self.chat_session.send_message(user_input).text

