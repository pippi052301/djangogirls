from learning.models import Attempt


def get_recent_average_score(user):
    """ユーザーの直近5問の平均点を返す。成績がなければ50を返す。"""

    return Attempt.objects.recent_average_score_for(
        user,
        limit=5,
    )


def generate_next_exercise_for_user(*, user, text_content):
    """DBで求めた平均点をAIへ渡し、次の1問を生成する。"""

    # AI担当のブランチが未統合でもDjangoを起動できるよう、
    # 実際にこの関数を呼び出すときにimportする。
    from ai_engine.services.adaptive_service import (
        generate_adaptive_practice,
    )

    recent_average_score = get_recent_average_score(user)

    return generate_adaptive_practice(
        text_content,
        recent_average_score=float(recent_average_score),
        total_questions=1,
    )