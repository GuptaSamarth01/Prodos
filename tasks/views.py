from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Task
from study.models import StudySession
from datetime import date
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

def register_view(request):
    if request.method == "POST":

        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Check password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("login")

        # Check username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("login")

        # Check email exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("login")

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Save full name
        user.first_name = full_name
        user.save()

        login(request, user)
        return redirect("dashboard")

    return redirect("login")
@login_required
def dashboard(request):

    # -------------------------
    # Handle Study Session Form
    # -------------------------
    if request.method == "POST":
        StudySession.objects.create(
            user=request.user,
            subject=request.POST.get('subject'),
            hours=float(request.POST.get('hours')),
            date=request.POST.get('date')
        )
        messages.success(request, "Study session added successfully!")
        return redirect('dashboard')

    # -------------------------
    # Fetch Data
    # -------------------------
    tasks = Task.objects.filter(user=request.user)
    study_sessions = StudySession.objects.filter(user=request.user)

    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='Completed').count()

    # Safe sum calculation
    total_study_hours = sum(session.hours for session in study_sessions)

    # -------------------------
    # Progress Calculation
    # -------------------------
    progress_percentage = 0
    if total_tasks > 0:
        progress_percentage = int((completed_tasks / total_tasks) * 100)

    # -------------------------
    # Productivity Score
    # Formula:
    # 60% task completion weight
    # 40% study consistency weight
    # -------------------------
    productivity_score = int(
        (progress_percentage * 0.6) +
        min(total_study_hours * 2, 40)  # Cap study contribution
    )

    # Cap score at 100
    productivity_score = min(productivity_score, 100)

    # -------------------------
    # Today's Tasks
    # -------------------------
    today = date.today()
    todays_tasks = tasks.filter(due_date=today)

    context = {
        'tasks': tasks,
        'study_sessions': study_sessions,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'total_study_hours': total_study_hours,
        'progress_percentage': progress_percentage,
        'productivity_score': productivity_score,
        'todays_tasks': todays_tasks,
    }

    return render(request, 'dashboard.html', context)


@login_required
def add_task(request):

    days_list = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    if request.method == "POST":

        selected_days = request.POST.getlist('days')
        days_string = ", ".join(selected_days) if selected_days else ""

        Task.objects.create(
            user=request.user,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            priority=request.POST.get('priority'),
            due_date=request.POST.get('due_date'),
            recurrence=request.POST.get('recurrence'),
            days=days_string
        )

        messages.success(request, "Task added successfully!")
        return redirect('dashboard')   

    return render(request, 'add_task.html', {
        'days_list': days_list
    })

@login_required
def complete_task(request, task_id):

    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.status = 'Completed'
    task.save()

    messages.success(request, "Task marked as completed!")
    return redirect('dashboard')


@login_required
def delete_task(request, task_id):

    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()

    messages.success(request, "Task deleted successfully!")
    return redirect('dashboard')