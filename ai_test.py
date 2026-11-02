import os
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

insights = {
    'worst_source': 'facebook',
    'worst_change': -747623,
    'best_source': 'affiliates',
    'best_change': -4058
}

load_dotenv(BASE_DIR / '.env')

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("API key loaded successfully")
else:
    print("API key not found")

if api_key:
    client = OpenAI(api_key=api_key)
    print("OpenAI client created successfully")

def build_ai_prompt(insights):

    data_json = json.dumps(insights, indent=4)

    prompt = f"""
    You are a professional Data Analyst.

    Analyze the following lending analytics data:

    {data_json}

    Instructions:
    1. Identify the main changes.
    2. Explain which traffic sources contributed to the decline.
    3. Do not invent numbers or reasons.
    4. Write a concise analytical summary in Ukrainian.
    5. Provide exactly 3 main analytical findings based on the data.
    6. Propose 2 hypotheses for further investigation.
    7. Keep the response under 150 words.
    """

    return prompt

final_prompt = build_ai_prompt(insights)

print(final_prompt)
print(type(final_prompt))
