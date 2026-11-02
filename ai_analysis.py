import json
import numpy as np
import pandas as pd


def convert_numpy(value):
    if isinstance(value, np.integer):
        return int(value)
    elif isinstance(value, np.floating):
        return float(value)
    elif isinstance(value, np.bool_):
        return bool(value)
    raise TypeError(f"Unsupported type: {type(value)}")


def clean_value(value):
    if pd.isna(value):
        return None
    elif isinstance(value, (np.integer, np.floating, np.bool_)):
        return convert_numpy(value)
    elif isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def clean_nested(value):
    if isinstance(value, dict):
        return {
            str(key): clean_nested(item)
            for key, item in value.items()
        }
    elif isinstance(value, list):
        return [clean_nested(item) for item in value]
    return clean_value(value)


def prepare_ai_data(pivot, insights):
    return {
        "summary": insights,
        "sources": pivot.reset_index().to_dict(orient="records")
    }


def build_ai_prompt(ai_data):
    clean_data = clean_nested(ai_data)

    data_json = json.dumps(
        clean_data,
        indent=4,
        ensure_ascii=False,
        allow_nan=False
    )

    return f"""
You are a professional Data Analyst.

Analyze the following lending analytics data:

{data_json}

Instructions:
1. Identify the main changes in issued amounts.
2. Explain which traffic sources contributed to the changes.
3. Do not invent numbers or causes.
4. Write in Ukrainian.
5. Provide exactly 3 analytical findings.
6. Propose 2 hypotheses for further investigation.
7. Keep the response under 150 words.
"""


def generate_ai_analysis(client, prompt):
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return response.output_text


def get_report_analysis(report, pivot, insights, client=None):
    if client is None:
        from main import generate_insights
        _, message = generate_insights(report)
        return message

    try:
        ai_data = prepare_ai_data(pivot, insights)
        prompt = build_ai_prompt(ai_data)
        return generate_ai_analysis(client, prompt)
    except Exception as e:
        print(f"AI unavailable: {e}")
        from main import generate_insights
        _, message = generate_insights(report)
        return message