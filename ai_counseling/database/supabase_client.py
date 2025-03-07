from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def store_conversation(user_id, user_input, bot_response, mood_score):
    data = {
        "user_id": user_id,
        "user_input": user_input,
        "bot_response": bot_response,
        "mood_score": mood_score,
    }
    return supabase.table("conversations").insert(data).execute()

def store_assessment(user_id, assessment):
    data = {
        "user_id": user_id,
        "assessment": assessment,
    }
    return supabase.table("mental_health_assessments").insert(data).execute()

def get_user_mood_scores(user_id):
    result = supabase.table("conversations").select("mood_score").eq("user_id", user_id).order("timestamp", desc=True).limit(10).execute()
    return [item['mood_score'] for item in result.data]

