from django import forms
from .models import QuizSchedule


class QuizScheduleForm(forms.ModelForm):

    class Meta:

        model = QuizSchedule

        fields = [
            "topic",
            "frequency",
<<<<<<< Updated upstream
            "time",
            "question_count",
=======
            "weekly_days",
            "specific_date",
            "start_time",
            "end_time",
            "priority",
>>>>>>> Stashed changes
            "difficulty",
        ]

        widgets = {

            "time": forms.TimeInput(
                attrs={
                    "type": "time"
                }
            ),

        }