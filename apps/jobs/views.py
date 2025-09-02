from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Job, Application, Category, JobBookmark, JobBrowseHistory
from .forms import JobForm, JobApplicationForm, JobSearchForm, JobPostForm
from django.shortcuts import render
from .models import Category
from apps.accounts.models import Employer

def companies(request):
    companies = Employer.objects.all()
    return render(request, 'jobs/companies.html', {'companies': companies})
def home(request):
    featured_jobs = Job.objects.filter(is_active=True)[:6]
    categories = Category.objects.all()
    context = {
        'featured_jobs': featured_jobs,
        'categories': categories,
    }
    return render(request, 'jobs/home.html', context)

def job_list(request):
    form = JobSearchForm(request.GET)
    jobs = Job.objects.filter(is_active=True)

    if form.is_valid():
        search = form.cleaned_data.get('search')
        location = form.cleaned_data.get('location')
        category = form.cleaned_data.get('category')
        job_type = form.cleaned_data.get('job_type')

        if search:
            jobs = jobs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        if location:
            jobs = jobs.filter(location__icontains=location)
        if category:
            jobs = jobs.filter(category=category)
        if job_type:
            jobs = jobs.filter(job_type=job_type)

    paginator = Paginator(jobs, 9)  # 9 jobs per page
    page = request.GET.get('page')
    jobs = paginator.get_page(page)

    context = {
        'jobs': jobs,
        'form': form,
    }
    return render(request, 'jobs/job_list.html', context)

def job_detail(request, job_id):
    import logging
    logger = logging.getLogger(__name__)
    
    job = get_object_or_404(Job, id=job_id, is_active=True)
    application_form = JobApplicationForm() if request.user.is_authenticated else None
    has_applied = False
    is_bookmarked = False

    if request.user.is_authenticated and hasattr(request.user, 'jobseeker'):
        has_applied = Application.objects.filter(
            job=job, job_seeker=request.user.jobseeker
        ).exists()
        is_bookmarked = JobBookmark.objects.filter(
            job=job, job_seeker=request.user.jobseeker
        ).exists()
        
        # 记录浏览历史
        try:
            # 获取用户IP地址
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            # 获取用户代理
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # 创建浏览历史记录
            JobBrowseHistory.objects.create(
                job=job,
                job_seeker=request.user.jobseeker,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            logger.info(f"Browse history recorded for job {job_id} by user {request.user.username}")
            
        except Exception as e:
            logger.error(f"Error recording browse history: {str(e)}", exc_info=True)

    context = {
        'job': job,
        'application_form': application_form,
        'has_applied': has_applied,
        'is_bookmarked': is_bookmarked,
    }
    return render(request, 'jobs/job_detail.html', context)

@login_required
def post_job(request):
    if not hasattr(request.user, 'employer'):
        return redirect('home')
        
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user.employer
            job.save()
            messages.success(request, "Job posted successfully!")
            return redirect('jobs:job_detail', job_id=job.id)
    else:
        form = JobForm()

    return render(request, 'jobs/post_job.html', {'form': form})

@login_required
def apply_job(request, job_id):
    if not request.user.is_job_seeker:
        messages.error(request, "Only job seekers can apply for jobs.")
        return redirect('jobs:job_detail', job_id=job_id)

    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    if Application.objects.filter(job=job, job_seeker=request.user.jobseeker).exists():
        messages.info(request, "You have already applied for this job.")
        return redirect('jobs:job_detail', job_id=job_id)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.job_seeker = request.user.jobseeker
            application.save()
            messages.success(request, "Application submitted successfully!")
            return redirect('dashboard:job_seeker_dashboard')

    return redirect('jobs:job_detail', job_id=job_id)

def search_jobs(request):
    form = JobSearchForm(request.GET)
    jobs = Job.objects.filter(is_active=True)

    if form.is_valid():
        search = form.cleaned_data.get('search')
        location = form.cleaned_data.get('location')
        category = form.cleaned_data.get('category')
        job_type = form.cleaned_data.get('job_type')

        if search:
            jobs = jobs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        if location:
            jobs = jobs.filter(location__icontains=location)
        if category:
            jobs = jobs.filter(category=category)
        if job_type:
            jobs = jobs.filter(job_type=job_type)

    paginator = Paginator(jobs, 9)  # 9 jobs per page
    page = request.GET.get('page')
    jobs = paginator.get_page(page)

    context = {
        'jobs': jobs,
        'form': form,
    }
    return render(request, 'jobs/search_results.html', context)

def categories(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'jobs/categories.html', context)

def company_detail(request, pk):
    company = get_object_or_404(Employer, pk=pk)
    active_jobs = Job.objects.filter(employer=company, is_active=True)
    
    context = {
        'company': company,
        'active_jobs': active_jobs,
    }
    return render(request, 'jobs/company_detail.html', context)

@login_required
@require_POST
def toggle_bookmark(request, job_id):
    """
    AJAX view to toggle job bookmark status
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Bookmark toggle request for job {job_id} by user {request.user.username}")
        
        if not hasattr(request.user, 'jobseeker'):
            logger.warning(f"User {request.user.username} is not a jobseeker")
            return JsonResponse({
                'success': False, 
                'message': '只有求职者可以收藏职位'
            })
        
        job = get_object_or_404(Job, id=job_id, is_active=True)
        job_seeker = request.user.jobseeker
        
        logger.info(f"Job found: {job.title}, JobSeeker: {job_seeker.user.username}")
        
        bookmark, created = JobBookmark.objects.get_or_create(
            job=job, 
            job_seeker=job_seeker
        )
        
        if not created:
            # Bookmark exists, remove it
            bookmark.delete()
            is_bookmarked = False
            message = '已取消收藏'
            logger.info(f"Bookmark removed for job {job_id}")
        else:
            # New bookmark created
            is_bookmarked = True
            message = '已添加到收藏'
            logger.info(f"Bookmark created for job {job_id}")
        
        response_data = {
            'success': True,
            'is_bookmarked': is_bookmarked,
            'message': message
        }
        
        logger.info(f"Bookmark toggle response: {response_data}")
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error in toggle_bookmark: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': '服务器错误，请重试'
        })