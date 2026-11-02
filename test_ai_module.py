import json
import numpy as np
import pandas as pd

from ai_analysis import prepare_ai_data, build_ai_prompt, get_report_analysis


pivot = pd.DataFrame({
    "2026-08": [100000, 80000],
    "2026-09": [90000, 70000],
    "change": [-10000, -10000]
}, index=pd.Index(["google", "facebook"], name="source"))

insights = {
    "latest_month": "2026-09",
    "previous_month": "2026-08",
    "worst_source": "google",
    "worst_change": np.int64(-10000),
    "best_source": "facebook",
    "best_change": np.int64(-10000)
}

ai_data = prepare_ai_data(pivot, insights)
prompt = build_ai_prompt(ai_data)

assert "google" in prompt
assert "facebook" in prompt
assert "2026-09" in prompt

print("JSON and prompt test: PASSED")


class FakeResponse:
    output_text = "Тестовий аналітичний висновок українською."


class FakeResponses:
    def create(self, model, input):
        return FakeResponse()


class FakeClient:
    responses = FakeResponses()


result = get_report_analysis(
    report=None,
    pivot=pivot,
    insights=insights,
    client=FakeClient()
)

assert result == "Тестовий аналітичний висновок українською."

print("AI response test: PASSED")
print(result)

class BrokenResponses:
    def create(self, model, input):
        raise RuntimeError("Simulated API failure")


class BrokenClient:
    responses = BrokenResponses()

test_report = pd.DataFrame({
    "year_month": ["2026-08", "2026-09"],
    "total_amount": [180000, 160000]
})

result = get_report_analysis(
    report=test_report,
    pivot=pivot,
    insights=insights,
    client=BrokenClient()
)

assert result == "In 2026-09, issued amount decreased by 11.11%."

print("API failure fallback test: PASSED")

result = get_report_analysis(
    report=test_report,
    pivot=pivot,
    insights=insights,
    client=None
)

assert result == "In 2026-09, issued amount decreased by 11.11%."

print("No API client fallback test: PASSED")