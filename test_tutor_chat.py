import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

import django
django.setup()
from django.conf import settings

if "testserver" not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append("testserver")
import json
from django.test import Client


client = Client()


# ==========================================
# 共通データ
# ==========================================

question_prompt = """
Explain the discriminant D in a quadratic equation
and describe how its value determines the number of real solutions.
"""

required_key_points = [
    "The discriminant is D = b² - 4ac.",
    "If D > 0, there are two distinct real solutions.",
    "If D = 0, there is one repeated real solution.",
    "If D < 0, there are no real solutions."
]


def send_tutor_request(student_input, history):
    data = {
        "student_input": student_input,
        "history": history,
        "question_prompt": question_prompt,
        "required_key_points": required_key_points
    }

    response = client.post(
        "/ai/tutor/chat/",
        data=json.dumps(data),
        content_type="application/json"
    )

    return response


# ==========================================
# Tutor-01
# 1つのKey Pointしか答えていない
# ==========================================

print("\n===== Tutor-01: Incomplete Answer =====")

response = send_tutor_request(
    student_input="The discriminant is D = b² - 4ac.",
    history=[]
)

print("Status:", response.status_code)

result = response.json()
print(json.dumps(result, indent=4, ensure_ascii=False))

# ==========================================
# Tutor-02
# 一部のKey Pointまで追加
# ==========================================

print("\n===== Tutor-02: Partially Complete =====")

history = [
    {
        "role": "user",
        "content": "The discriminant is D = b² - 4ac."
    },
    {
        "role": "model",
        "content": "How does the value of D affect the number of real solutions?"
    }
]

response = send_tutor_request(
    student_input="""
    If D > 0, there are two distinct real solutions.
    """,
    history=history
)

print("Status:", response.status_code)

result = response.json()
print(json.dumps(result, indent=4, ensure_ascii=False))

# ==========================================
# Tutor-03
# 残りのKey Pointも回答
# ==========================================

print("\n===== Tutor-03: Complete Answer =====")

history = [
    {
        "role": "user",
        "content": "The discriminant is D = b² - 4ac."
    },
    {
        "role": "model",
        "content": "How does the value of D affect the number of real solutions?"
    },
    {
        "role": "user",
        "content": "If D > 0, there are two distinct real solutions."
    },
    {
        "role": "model",
        "content": "Good. What happens when D is zero or negative?"
    }
]

response = send_tutor_request(
    student_input="""
    If D = 0, there is one repeated real solution.
    If D < 0, there are no real solutions.
    """,
    history=history
)

print("Status:", response.status_code)

result = response.json()
print(json.dumps(result, indent=4, ensure_ascii=False))

# ==========================================
# Tutor-04
# 完成答案を要求する
# ==========================================

print("\n===== Tutor-04: Ask for Full Answer =====")

response = send_tutor_request(
    student_input="I don't know. Please give me the full answer.",
    history=[]
)

print("Status:", response.status_code)

result = response.json()
print(json.dumps(result, indent=4, ensure_ascii=False))