from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Workout, Record
from .forms import WorkoutUploadForm
from fitparse import FitFile
import gzip


@login_required
def dashboard(request):
    workouts = Workout.objects.filter(user=request.user)
    return render(request, "dashboard.html", {"workouts": workouts})


@login_required
def upload_workout(request):
    if request.method == "POST":
        form = WorkoutUploadForm(request.POST, request.FILES)
        if form.is_valid():
            workout = form.save(commit=False)
            workout.user = request.user
            workout.save()
            process_fit_file(workout.file_path, workout)
            return redirect("workouts:dashboard")
    else:
        form = WorkoutUploadForm()
    return render(request, "upload.html", {"form": form})


@login_required
def view_workout(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    records = Record.objects.filter(workout=workout)
    return render(
        request, "workout_detail.html", {"workout": workout, "records": records}
    )


def process_fit_file(file_path, workout):
    """Parses the .fit file and saves data to the database"""
    if file_path.endswith(".gz"):
        with gzip.open(file_path, "rb") as f:
            fitfile = FitFile(f.read())
    else:
        fitfile = FitFile(file_path)

    for record in fitfile.get_messages("record"):
        Record.objects.create(
            workout=workout,
            timestamp=record.get("timestamp", None),
            position_lat=record.get("position_lat", None),
            position_long=record.get("position_long", None),
            gps_accuracy=record.get("gps_accuracy", None),
            altitude=record.get("altitude", None),
            distance=record.get("distance", None),
            heart_rate=record.get("heart_rate", None),
            speed=record.get("speed", None),
            calories=record.get("calories", None),
        )
