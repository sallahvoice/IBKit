"""
Large Language Model integration module using Google's Gemini API.
Provides functionality to analyze financial data with AI-powered insights.
"""

import os

import google.generativeai as genai
from dotenv import load_dotenv

from backend.exceptions import GeminiError
from backend.utils.logger import get_logger

logger = get_logger(__file__)

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI-API-KEY"))
model = genai.GenerativeModel(model_name="gemini-2.5-flash")


def extract_info_gemini(df, user_prompt):
    """AI model receives a df & a user prompt & answer the prompt"""
    text_csv = df.to_csv(index=False)

    prompt = f"""i will provide you with financial data for a certain
    publicly traded company in a csv format.
    csv: {text_csv}
    now answer this:
    {user_prompt}
    only give precise & relevant part."""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except GeminiError as e:
        logger.error("[gemini error] %s", e)
        return "An error occurred while processing the data."
