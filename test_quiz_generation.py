from ai_engine.services.quiz_service import generate_quiz_from_text
from ai_engine.services.adaptive_service import generate_adaptive_practice


# ==================================================
# テスト用教材
# ==================================================

sample_text = """
DjangoはPythonで作られたWebフレームワークです。

DjangoではMVTアーキテクチャが採用されています。

Modelはアプリケーションで使用するデータを管理し、
データベースへの保存や取得を担当します。

Viewはユーザーからのリクエストを受け取り、
必要な処理を行います。

TemplateはHTMLなどを使用して、
ユーザーに表示する画面を担当します。
"""


# ==================================================
# TEST 1
# 通常の選択式問題生成
# ==================================================

print("\n======================================")
print("TEST 1: 選択式問題生成")
print("======================================")

quiz_result = generate_quiz_from_text(
    sample_text,
    num_questions=2
)

if quiz_result is None:
    print("❌ FAIL: 問題を生成できませんでした")

else:
    print(f"生成された問題数: {len(quiz_result)}")

    for i, quiz in enumerate(quiz_result, start=1):

        print(f"\n--- 問題 {i} ---")

        print("問題:")
        print(quiz.get("question"))

        print("\n選択肢:")
        options = quiz.get("options", {})

        for key, value in options.items():
            print(f"{key}: {value}")

        print("\n正解:")
        print(quiz.get("correct_answer"))

        print("\n解説:")
        print(quiz.get("explanation"))


# ==================================================
# TEST 2
# Adaptive問題生成
# ==================================================

print("\n\n======================================")
print("TEST 2: Adaptive問題生成")
print("======================================")

adaptive_result = generate_adaptive_practice(
    topic_name="Django MVT",
    recent_average_score=80,
    source_text=sample_text
)

if adaptive_result is None:
    print("❌ FAIL: Adaptive問題を生成できませんでした")

else:

    print("\n生成された問題:")

    for i, question in enumerate(adaptive_result, start=1):

        print(f"\n---------- 問題 {i} ----------")

        print("タイプ:")
        print(question.get("type"))

        print("\n問題:")
        print(question.get("question"))

        # 選択式
        if question.get("type") == "multiple_choice":

            print("\n選択肢:")

            options = question.get("options", {})

            for key, value in options.items():
                print(f"{key}: {value}")

            print("\n正解:")
            print(question.get("correct_answer"))

        # 短答式
        elif question.get("type") == "short_answer":

            print("\n模範解答:")
            print(question.get("sample_answer"))

        # 長答式・記述式
        elif question.get("type") == "long_answer":

            print("\n必要なキーポイント:")

            key_points = question.get("key_points", [])

            for point in key_points:
                print(f"- {point}")

        print("\n解説:")
        print(question.get("explanation"))


    # ==================================================
    # 問題形式ごとの個数確認
    # ==================================================

    mc_count = 0
    short_count = 0
    long_count = 0

    for question in adaptive_result:

        if question.get("type") == "multiple_choice":
            mc_count += 1

        elif question.get("type") == "short_answer":
            short_count += 1

        elif question.get("type") == "long_answer":
            long_count += 1


    print("\n======================================")
    print("問題数チェック")
    print("======================================")

    print(f"選択式     : {mc_count}")
    print(f"短答式     : {short_count}")
    print(f"長答式     : {long_count}")


    # score=80 の期待値
    if mc_count == 1:
        print("✅ 選択式: PASS")
    else:
        print("❌ 選択式: FAIL")

    if short_count == 2:
        print("✅ 短答式: PASS")
    else:
        print("❌ 短答式: FAIL")

    if long_count == 2:
        print("✅ 長答式: PASS")
    else:
        print("❌ 長答式: FAIL")