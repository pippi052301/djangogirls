from django import forms
from .models import QuizSchedule


class QuizScheduleForm(forms.ModelForm):
    weekly_days = forms.CharField(required=False)
    specific_date = forms.DateField(required=False)
    start_time = forms.TimeField(required=False)
    end_time = forms.TimeField(required=False)
    target_resource = forms.CharField(required=False)
    priority = forms.IntegerField(required=False, initial=3)

    class Meta:
        model = QuizSchedule
        fields = [
            "topic",
            "frequency",
            "weekly_days",
            "specific_date",
            "start_time",
            "end_time",
            "priority",
            "target_resource",
        ]