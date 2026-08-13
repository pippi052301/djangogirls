from ai_engine.services.quiz_service import generate_quiz_from_text


sample_text = """
DjangoはPythonで作られたWebフレームワークです。
DjangoはMVTアーキテクチャを採用しています。
Modelはデータを管理し、
Viewは処理を担当し、
Templateは画面表示を担当します。
"""


result = generate_quiz_from_text(
    sample_text,
    num_questions=2
)


print("===== 問題生成テスト =====")

if result is None:
    print("❌ FAIL: 問題を生成できませんでした")

else:
    print(f"生成された問題数: {len(result)}")

    for i, quiz in enumerate(result, start=1):

        print(f"\n--- 問題 {i} ---")
        print("問題:", quiz.get("question"))
        print("選択肢:", quiz.get("options"))
        print("正解:", quiz.get("correct_answer"))
        print("解説:", quiz.get("explanation"))