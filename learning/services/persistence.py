from collections.abc import Mapping, Sequence
from decimal import Decimal, InvalidOperation

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from learning.models import (
    Attempt,
    Exercise,
    MapEdge,
    MapNode,
    Quiz,
    QuizAttempt,
)


def _score_as_decimal(value, *, field_name):
    try:
        score = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValidationError({field_name: "A numeric score is required."}) from exc

    if not 0 <= score <= 100:
        raise ValidationError({field_name: "The score must be between 0 and 100."})

    return score


def _require_mapping(value, *, field_name):
    if not isinstance(value, Mapping):
        raise ValidationError({field_name: "A JSON object is required."})

    return value


def _require_sequence(value, *, field_name):
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValidationError({field_name: "A JSON array is required."})

    return value


@transaction.atomic
def save_generated_quiz(
    *,
    note,
    title,
    questions,
    recent_average_score=50,
):
    """Save one AI-generated quiz and all of its exercises atomically."""

    questions = _require_sequence(questions, field_name="questions")
    if not questions:
        raise ValidationError({"questions": "At least one question is required."})

    title = str(title).strip()
    if not title:
        raise ValidationError({"title": "A quiz title is required."})

    average_score = _score_as_decimal(
        recent_average_score,
        field_name="recent_average_score",
    )
    quiz = Quiz.objects.create(note=note, title=title)

    for order, raw_question in enumerate(questions, start=1):
        question_data = _require_mapping(
            raw_question,
            field_name=f"questions[{order - 1}]",
        )
        question_type = question_data.get(
            "type",
            question_data.get(
                "question_type",
                Exercise.QuestionType.MULTIPLE_CHOICE,
            ),
        )
        correct_answer = question_data.get("correct_answer")
        if correct_answer in (None, ""):
            correct_answer = question_data.get("sample_answer", "")

        Exercise.objects.create(
            quiz=quiz,
            order=order,
            question_type=question_type,
            difficulty=question_data.get("difficulty", 50),
            recent_average_score=average_score,
            question=question_data.get("question", ""),
            options=question_data.get("options", {}),
            correct_answer=correct_answer,
            key_points=question_data.get("key_points", []),
            hints=question_data.get("hints", []),
            explanation=question_data.get("explanation", ""),
        )

    return quiz


@transaction.atomic
def replace_knowledge_graph(*, note, graph_data):
    """Replace a note's knowledge graph with one validated AI response."""

    graph_data = _require_mapping(graph_data, field_name="graph_data")
    nodes_data = _require_sequence(
        graph_data.get("nodes", []),
        field_name="nodes",
    )
    edges_data = _require_sequence(
        graph_data.get("edges", []),
        field_name="edges",
    )

    MapNode.objects.filter(note=note).delete()

    nodes_by_key = {}
    created_nodes = []
    for index, raw_node in enumerate(nodes_data):
        node_data = _require_mapping(raw_node, field_name=f"nodes[{index}]")
        key = str(node_data.get("id", node_data.get("key", ""))).strip()
        label = str(node_data.get("label", "")).strip()

        if not key or not label:
            raise ValidationError(
                {f"nodes[{index}]": "Both id and label are required."}
            )
        if key in nodes_by_key:
            raise ValidationError({f"nodes[{index}].id": "Node ids must be unique."})

        node = MapNode.objects.create(note=note, key=key, label=label)
        nodes_by_key[key] = node
        created_nodes.append(node)

    created_edges = []
    for index, raw_edge in enumerate(edges_data):
        edge_data = _require_mapping(raw_edge, field_name=f"edges[{index}]")
        source_key = str(
            edge_data.get("from", edge_data.get("source", ""))
        ).strip()
        target_key = str(
            edge_data.get("to", edge_data.get("target", ""))
        ).strip()

        source = nodes_by_key.get(source_key)
        target = nodes_by_key.get(target_key)
        if source is None or target is None:
            raise ValidationError(
                {f"edges[{index}]": "Every edge must reference existing node ids."}
            )

        created_edges.append(
            MapEdge.objects.create(
                source=source,
                target=target,
                label=str(edge_data.get("label", "")).strip(),
            )
        )

    return created_nodes, created_edges


def start_quiz_attempt(*, user, quiz):
    """Start an attempt only when the quiz belongs to the requesting user."""

    if quiz.note.owner_id != user.pk:
        raise PermissionDenied("This user cannot start the selected quiz.")

    return QuizAttempt.objects.create(user=user, quiz=quiz)


@transaction.atomic
def save_answer(
    *,
    quiz_attempt,
    exercise,
    user_answer,
    reasoning,
    used_hint_count=0,
):
    """Create or update one answer and complete the quiz when all answers exist."""

    attempt, _ = Attempt.objects.update_or_create(
        quiz_attempt=quiz_attempt,
        exercise=exercise,
        defaults={
            "user_answer": user_answer,
            "reasoning": reasoning,
            "used_hint_count": used_hint_count,
        },
    )

    exercise_count = quiz_attempt.quiz.exercises.count()
    answer_count = quiz_attempt.answers.count()
    if exercise_count and answer_count >= exercise_count:
        quiz_attempt.completed_at = timezone.now()
        quiz_attempt.save(update_fields=["completed_at"])

    return attempt


def apply_grading_result(*, attempt, grading_data):
    """Normalize an AI grading response and apply it to an existing answer."""

    grading_data = _require_mapping(grading_data, field_name="grading_data")
    raw_score = grading_data.get("total_score", grading_data.get("score"))
    if raw_score is None:
        raise ValidationError({"grading_data": "A score is required."})

    attempt.score = _score_as_decimal(raw_score, field_name="score")
    attempt.feedback = str(
        grading_data.get(
            "overall_feedback",
            grading_data.get("feedback", ""),
        )
    )
    attempt.rubric_details = dict(grading_data)
    attempt.save(update_fields=["score", "feedback", "rubric_details"])
    return attempt
