from ai_engine.services.embedding_service import get_text_embedding
import math


def cosine_similarity(vec1, vec2):
    dot_product = sum(a * b for a, b in zip(vec1, vec2))

    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))

    return dot_product / (norm1 * norm2)


text_a = """
DjangoのModelはデータやデータベースを管理する。
"""

text_b = """
Modelはデータベースとのやり取りを担当する。
"""

text_c = """
サッカーでは2つのチームがボールを使って試合をする。
"""


print("⏳ Embeddingを生成中...")

vector_a = get_text_embedding(text_a)
vector_b = get_text_embedding(text_b)
vector_c = get_text_embedding(text_c)


if vector_a and vector_b and vector_c:

    similarity_ab = cosine_similarity(vector_a, vector_b)
    similarity_ac = cosine_similarity(vector_a, vector_c)

    print("\n=== 類似度テスト結果 ===")

    print(f"A-B 類似度: {similarity_ab}")
    print(f"A-C 類似度: {similarity_ac}")

    if similarity_ab > similarity_ac:
        print("\n✅ 成功：意味が近い文章の方が高い類似度になりました。")
    else:
        print("\n❌ 想定外：関係のない文章の方が高い類似度になっています。")

else:
    print("❌ Embeddingの生成に失敗しました。")