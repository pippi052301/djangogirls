from django import forms
from .models import QuizSchedule


class QuizScheduleForm(forms.ModelForm):

    class Meta:

        model = QuizSchedule

        fields = [
            "topic",
            "frequency",
            "weekly_days",
            "start_time",
            "end_time",
            "priority",
            "difficulty",
            "note",
            "folder",
        ]

        widgets = {
            "start_time": forms.TimeInput(
                attrs={
                    "type": "time"
                }
            ),
            "end_time": forms.TimeInput(
                attrs={
                    "type": "time"
                }
            ),
        }