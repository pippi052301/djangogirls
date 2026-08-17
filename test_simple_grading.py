from ai_engine.services.adaptive_service import grade_simple_answer


# ==========================================
# 選択式テスト
# ==========================================

question = """
DjangoのMVTにおいて、
データベースとのやり取りを主に担当するものはどれですか？

A. View
B. Model
C. Template
D. URL
"""

correct_answer = "B"

explanation = """
Modelはデータを管理し、
データベースとのやり取りを担当する。
"""


multiple_choice_tests = [
    ("MC-01 正解", "B"),
    ("MC-02 不正解", "C"),
    ("MC-03 小文字", "b"),
    ("MC-04 空白あり", " B "),
]


print("===== 選択式テスト =====")

for test_name, student_answer in multiple_choice_tests:

    result = grade_simple_answer(
        question_type="multiple_choice",
        question=question,
        user_answer=student_answer,
        correct_answer=correct_answer,
        explanation=explanation
    )

    print(f"\n{test_name}")
    print(result)


# ==========================================
# 短答式テスト
# ==========================================

question = """
Briefly explain the role of the Model in Django's MVT architecture.
"""

correct_answer = """
The Model manages data and handles interactions with the database.
"""

explanation = """
The Model defines the data structure of an application and is responsible for operations such as storing and retrieving data from the database.
"""


short_answer_tests = [
    (
        "SA-06 Blank Answer",
        ""
    )
]


print("\n===== 短答式テスト =====")

for test_name, student_answer in short_answer_tests:

    result = grade_simple_answer(
        question_type="short_answer",
        question=question,
        user_answer=student_answer,
        correct_answer=correct_answer,
        explanation=explanation
    )

    print(f"\n{test_name}")
    print(result)