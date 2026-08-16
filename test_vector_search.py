from ai_engine.services.embedding_service import get_text_embedding
import math


# コサイン類似度を計算する関数
def cosine_similarity(vec1, vec2):
    dot_product = sum(a * b for a, b in zip(vec1, vec2))

    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))

    return dot_product / (norm1 * norm2)


# ==========================================
# 新しく提出された学生答案
# ==========================================

student_answer = """
DjangoのModelはデータを管理し、
データベースとのやり取りを担当する。
Viewは処理のロジックを担当する。
Templateはユーザーに表示する画面を担当する。
"""


# ==========================================
# DBの代わりに用意する採点済みサンプル答案
# ==========================================

sample_answers = [
    {
        "id": "Sample-01",
        "answer": """
        DjangoのModelはデータベースとのやり取りを担当し、
        Viewはアプリケーションの処理を担当する。
        TemplateはHTMLなどを用いて画面を表示する。
        """,
        "score": 95
    },

    {
        "id": "Sample-02",
        "answer": """
        DjangoではModelがデータを扱い、
        Viewが処理を行い、
        Templateが画面を表示する。
        """,
        "score": 80
    },

    {
        "id": "Sample-03",
        "answer": """
        DjangoにはModel、View、Templateという
        3つの部分がある。
        """,
        "score": 55
    },

    {
        "id": "Sample-04",
        "answer": """
        DjangoはPythonでWebサイトを作るための
        フレームワークである。
        """,
        "score": 35
    },

    {
        "id": "Sample-05",
        "answer": """
        サッカーは2つのチームが
        ボールを使って行うスポーツである。
        """,
        "score": 10
    }
]


print("⏳ 学生答案をEmbeddingに変換中...")

student_vector = get_text_embedding(student_answer)

results = []


# ==========================================
# 各サンプル答案との類似度を計算
# ==========================================

for sample in sample_answers:

    print(f"⏳ {sample['id']} を比較中...")

    sample_vector = get_text_embedding(sample["answer"])

    similarity = cosine_similarity(
        student_vector,
        sample_vector
    )

    results.append({
        "id": sample["id"],
        "answer": sample["answer"],
        "score": sample["score"],
        "similarity": similarity
    })


# ==========================================
# 類似度が高い順に並べる
# ==========================================

results.sort(
    key=lambda x: x["similarity"],
    reverse=True
)


# ==========================================
# Top 3を取得
# ==========================================

top_3 = results[:3]


print("\n==============================")
print("🔍 類似答案 Top 3")
print("==============================")


for rank, result in enumerate(top_3, start=1):

    print(f"\n--- 第{rank}位 ---")

    print(f"ID: {result['id']}")

    print(
        f"類似度: "
        f"{result['similarity']:.4f}"
    )

    print(
        f"人間による採点: "
        f"{result['score']}点"
    )

    print(
        f"答案: "
        f"{result['answer']}"
    )