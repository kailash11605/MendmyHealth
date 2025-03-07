from config import MAX_CONVERSATION_HISTORY
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

def update_conversation_history(history, user_input, bot_response):
    history.append(f"User: {user_input}")
    history.append(f"Bot: {bot_response}")
    
    if len(history) > MAX_CONVERSATION_HISTORY:
        history = history[-MAX_CONVERSATION_HISTORY:]
    
    return history

def calculate_mood_score(text):
    sentiment = sia.polarity_scores(text)
    return (sentiment['compound'] + 1) * 5  # Convert [-1, 1] to [0, 10]

