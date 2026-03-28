import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))



def get_gemini_suggestions(resume_text, job_desc):

    try:
        if not resume_text.strip():
            return "⚠️ Resume text is empty. Cannot generate suggestions."

        resume_text = resume_text[:3000]   # limit length
        job_desc = job_desc[:1500]
        
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
        Analyze the resume and job description.

        Resume:
        {resume_text}

        Job Description:
        {job_desc}

        Give improvement suggestions.
        """

        response = model.generate_content(prompt)
        
        if response and hasattr(response, "text"):
            try:
                return response.text
            except:
                return "⚠️ AI response parsing failed"

        return "⚠️ No response from AI"

    except Exception as e:
        
        return f"⚠️ Gemini Error: {str(e)}"
