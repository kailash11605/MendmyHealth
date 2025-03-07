import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

class VideoAnalyzer:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')

    def analyze_content(self, labels):
        try:
            prompt = f"""
            Analyze the following video content labels and provide:
            1. A score from 1-10 based on the overall mental health impact, where 1 is very negative and 10 is very positive.
            2. A brief analysis of the potential mental health effects of this content.
            3. Suggestions for maintaining a healthy balance when consuming such content.

            Video content labels: {', '.join(labels)}

            Format your response as follows:
            Score: [1-10]
            Analysis: [Brief analysis]
            Recommendations: [Suggestions for healthy consumption]
            """

            response = self.model.generate_content(prompt)
            analysis = response.text
            
            # Extract the score from the analysis
            score_line = [line for line in analysis.split('\n') if line.startswith('Score:')][0]
            score = int(score_line.split(':')[1].strip())

            return score, analysis

        except Exception as e:
            print(f"An error occurred during content analysis: {str(e)}")
            return None, "Error: Unable to analyze the content. Please try again."

    def get_content_safety(self, labels):
        try:
            prompt = f"""
            Analyze the following video content labels for any themes or elements that might be inappropriate or harmful:

            Video content labels: {', '.join(labels)}

            Provide a brief safety assessment of the content.
            """

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            print(f"An error occurred during content safety check: {str(e)}")
            return "Error: Unable to perform content safety check. Please try again."

