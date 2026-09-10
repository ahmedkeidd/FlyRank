import json
import requests

with open("llm/evals/cases.json", "r", encoding="utf-8-sig") as f:
    cases = json.load(f)

correct = 0
failures = []

for i, case in enumerate(cases):
    response = requests.post(
        "http://localhost:8000/enrich",
        json=case["input"],
        timeout=35
    )

    if response.status_code != 200:
        failures.append({"case": i, "reason": f"status {response.status_code}"})
        continue

    result = response.json()
    actual = result.get("category")
    expected = case["expected_category"]

    if actual == expected:
        correct += 1
    else:
        failures.append({"case": i, "expected": expected, "actual": actual})

total = len(cases)
print(f"score: {correct}/{total}")
print("failures:", failures)