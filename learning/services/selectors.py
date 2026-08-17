from learning.models import Attempt, MapNode, Quiz, QuizAttempt


def get_quiz_for_user(*, quiz_id, user):
    """Return one quiz with its exercises, restricted to the note owner."""

    return (
        Quiz.objects.select_related("note", "note__owner")
        .prefetch_related("exercises")
        .get(pk=quiz_id, note__owner=user)
    )


def get_quiz_attempt_for_user(*, quiz_attempt_id, user):
    """Return one attempt and its answers, restricted to the participating user."""

    return (
        QuizAttempt.objects.select_related("quiz", "quiz__note")
        .prefetch_related("answers", "answers__exercise")
        .get(pk=quiz_attempt_id, user=user)
    )


def list_quiz_attempts_for_user(*, user):
    """Return the user's quiz history without N+1 queries for quiz and note."""

    return QuizAttempt.objects.filter(user=user).select_related("quiz", "quiz__note")


def get_knowledge_graph_for_note(*, note):
    """Return a note's nodes with outgoing edges and their targets prefetched."""

    return (
        MapNode.objects.filter(note=note)
        .prefetch_related("outgoing_edges", "outgoing_edges__target")
        .order_by("id")
    )


def get_recent_average_score(*, user, limit=5):
    """Return the user's recent graded-answer average using the model QuerySet."""

    return Attempt.objects.recent_average_score_for(user=user, limit=limit)
