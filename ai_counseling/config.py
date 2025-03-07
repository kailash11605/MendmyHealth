import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

CHATBOT_MODEL_NAME = "gemini-pro"
ASSESSMENT_MODEL_NAME = "gemini-pro"

MAX_CONVERSATION_HISTORY = 20

# Flask configuration
SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

