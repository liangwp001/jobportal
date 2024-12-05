from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie
from .forms import EmployerSignUpForm, JobSeekerSignUpForm
from .models import CustomUser, JobSeeker, Employer
from apps.jobs.models import Application

@ensure_csrf_cookie
def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type', 'job_seeker')

        try:
            user = CustomUser.objects.get(
                Q(username=username_or_email) | Q(email=username_or_email)
            )
            if user_type == 'job_seeker' and not user.is_job_seeker:
                messages.error(request, "Please select the correct user type (Job Seeker).")
                return render(request, 'accounts/login.html')
            elif user_type == 'employer' and not user.is_employer:
                messages.error(request, "Please select the correct user type (Employer).")
                return render(request, 'accounts/login.html')

            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                if user.is_employer:
                    return redirect('dashboard:employer_dashboard')
                return redirect('dashboard:jobseeker_dashboard')
            else:
                messages.error(request, "Invalid password.")
        except CustomUser.DoesNotExist:
            messages.error(request, "No account found with these credentials.")
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def profile_view(request):
    if request.user.is_employer:
        return redirect('dashboard:employer_dashboard')
    elif request.user.is_job_seeker:
        return redirect('dashboard:jobseeker_dashboard')
    return redirect('home')

def employer_signup(request):
    if request.method == 'POST':
        form = EmployerSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Your employer account has been created.')
            return redirect('dashboard:employer_dashboard')
    else:
        form = EmployerSignUpForm()
    return render(request, 'accounts/signup_employer.html', {'form': form})

def jobseeker_signup(request):
    if request.method == 'POST':
        form = JobSeekerSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Your job seeker account has been created.')
            return redirect('dashboard:jobseeker_dashboard')
    else:
        form = JobSeekerSignUpForm()
    return render(request, 'accounts/signup_jobseeker.html', {'form': form})

def signup_view(request):
    return render(request, 'accounts/signup_choice.html')

@login_required
def user_profile(request):
    if not request.user.is_job_seeker:
        messages.error(request, "Access denied. Job seeker account required.")
        return redirect('home')
    
    context = {
        'user': request.user,
        'jobseeker': request.user.jobseeker,
        'applications': Application.objects.filter(job_seeker=request.user.jobseeker)
    }
    return render(request, 'accounts/user_profile.html', context)

@login_required
def employer_profile(request):
    if not request.user.is_employer:
        messages.error(request, "Access denied. Employer account required.")
        return redirect('home')
    
    context = {
        'user': request.user,
        'employer': request.user.employer,
        'jobs': request.user.employer.jobs.all()
    }
    return render(request, 'accounts/employer_profile.html', context)