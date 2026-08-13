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
DjangoのMVTにおけるModelの役割を簡潔に説明してください。
"""

correct_answer = """
Modelはデータを管理し、
データベースとのやり取りを担当する。
"""

explanation = """
Modelはアプリケーションのデータ構造を定義し、
データベースへの保存や取得などを担当する。
"""


short_answer_tests = [
    (
        "SA-05 明確な誤答",
        "ModelはHTMLを使ってユーザーに表示するWebページを作成する役割を持つ。"
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