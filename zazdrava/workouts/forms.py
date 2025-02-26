from django import forms
from .models import Workout


class WorkoutUploadForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ["workout_name"]
