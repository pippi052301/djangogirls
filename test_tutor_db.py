import os
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

import django
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client

from notes.models import Note
from learning.models import (
    Quiz,
    Exercise,
    TutorSession,
    TutorMessage,
)


# =========================
# Django Test Client 用設定
# =========================

if "testserver" not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append("testserver")


User = get_user_model()


# =========================
# 1. テストユーザー作成
# =========================

user, _ = User.objects.get_or_create(
    username="tutor_test_user"
)

user.set_password("testpass123")
user.save()


# =========================
# 2. テスト用 Note 作成
# =========================

note = Note.objects.create(
    owner=user,
    title="AI Tutor DB Test Note",
    content={
        "body": (
            "Django is a Python web framework "
            "used for developing web applications."
        )
    },
)


# =========================
# 3. テスト用 Quiz 作成
# =========================

quiz = Quiz.objects.create(
    note=note,
    title="AI Tutor DB Test",
)


# =========================
# 4. 記述式 Exercise 作成
# =========================

exercise = Exercise.objects.create(
    quiz=quiz,
    order=1,
    question_type=Exercise.QuestionType.LONG_ANSWER,
    question="What is Django?",
    key_points=[
        "Django is a Python web framework",
        "It is used to develop web applications",
    ],
)


# =========================
# 5. Login
# =========================

client = Client()

login_success = client.login(
    username="tutor_test_user",
    password="testpass123",
)

print("Login:", login_success)

if not login_success:
    print("❌ Login failed.")
    exit()


# =========================
# 6. Tutor 1ターン目
# =========================

response1 = client.post(
    "/ai/tutor/chat/",
    data=json.dumps({
        "exercise_id": exercise.id,
        "student_input": "Django is a Python framework.",
    }),
    content_type="application/json",
)

print("\n===== TURN 1 =====")
print("Status:", response1.status_code)
print("Response:", response1.content.decode())

if response1.status_code != 200:
    print("\n❌ 1ターン目で失敗しました。")
    exit()


data1 = response1.json()
session_id = data1["session_id"]

print("Session ID:", session_id)


# =========================
# 7. Tutor 2ターン目
# =========================

response2 = client.post(
    "/ai/tutor/chat/",
    data=json.dumps({
        "session_id": session_id,
        "student_input": (
            "It is used to develop web applications."
        ),
    }),
    content_type="application/json",
)

print("\n===== TURN 2 =====")
print("Status:", response2.status_code)
print("Response:", response2.content.decode())

if response2.status_code != 200:
    print("\n❌ 2ターン目で失敗しました。")
    exit()


# =========================
# 8. DB確認
# =========================

print("\n===== DATABASE =====")

session = TutorSession.objects.get(
    id=session_id
)

print("\nTutorSession:")
print(session)

print("\nReady for grading:")
print(session.is_ready_for_grading)

print("\nCompiled final answer:")
print(session.compiled_final_answer)


# =========================
# 9. TutorMessage確認
# =========================

messages = TutorMessage.objects.filter(
    session=session
).order_by("created_at", "id")

print("\nTutorMessages:")

for message in messages:
    print(
        f"{message.role}: {message.content}"
    )

print("\nMessage count:", messages.count())


# =========================
# 10. 判定
# =========================

print("\n===== RESULT =====")

if messages.count() == 4:
    print("✅ Tutor conversation was saved correctly.")
else:
    print(
        "⚠️ Expected 4 messages, "
        f"but found {messages.count()}."
    )

if TutorSession.objects.filter(id=session_id).exists():
    print("✅ TutorSession exists in DB.")
else:
    print("❌ TutorSession was not saved.")