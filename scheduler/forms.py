from django import forms
from .models import QuizSchedule


class QuizScheduleForm(forms.ModelForm):

    class Meta:

        model = QuizSchedule

        fields = [
            "topic",
            "frequency",
            "time",
            "question_count",
            "difficulty",
        ]

        widgets = {

            "time": forms.TimeInput(
                attrs={
                    "type": "time"
                }
            ),

        }