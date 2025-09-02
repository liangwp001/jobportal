from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.jobs.models import Job, Application, JobBookmark, JobBrowseHistory
from django.shortcuts import render

def home(request):
    return render(request, 'dashboard/home.html')

@login_required
def employer_dashboard(request):
    if not request.user.is_employer:
        messages.error(request, "Access denied. Employer account required.")
        return redirect('jobs:home')
    
    posted_jobs = Job.objects.filter(employer=request.user.employer)
    recent_applications = Application.objects.filter(
        job__employer=request.user.employer
    ).order_by('-applied_date')[:5]
    
    context = {
        'posted_jobs': posted_jobs,
        'recent_applications': recent_applications,
        'total_jobs': posted_jobs.count(),
        'total_applications': Application.objects.filter(
            job__employer=request.user.employer
        ).count(),
    }
    return render(request, 'dashboard/employer_dashboard.html', context)

@login_required
def job_seeker_dashboard(request):
    if not request.user.is_job_seeker:
        messages.error(request, "Access denied. Job seeker account required.")
        return redirect('jobs:home')
    
    applications = Application.objects.filter(
        job_seeker=request.user.jobseeker
    ).order_by('-applied_date')
    
    bookmarks = JobBookmark.objects.filter(
        job_seeker=request.user.jobseeker
    ).order_by('-created_date')
    
    # 获取浏览历史，去重并限制数量
    browse_history = JobBrowseHistory.objects.filter(
        job_seeker=request.user.jobseeker
    ).select_related('job').order_by('-browsed_date')[:20]  # 限制显示最近20条
    
    # 去重处理，只显示每个职位最近一次浏览
    seen_jobs = set()
    unique_browse_history = []
    for history in browse_history:
        if history.job.id not in seen_jobs:
            unique_browse_history.append(history)
            seen_jobs.add(history.job.id)
    
    context = {
        'applications': applications,
        'bookmarks': bookmarks,
        'browse_history': unique_browse_history,
        'total_applications': applications.count(),
        'total_bookmarks': bookmarks.count(),
        'total_browse_history': len(unique_browse_history),
        'pending_applications': applications.filter(status='pending').count(),
        'accepted_applications': applications.filter(status='accepted').count(),
    }
    return render(request, 'dashboard/job_seeker_dashboard.html', context)

@login_required
def manage_application(request, application_id):
    if not request.user.is_employer:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    application = Application.objects.get(
        id=application_id,
        job__employer=request.user.employer
    )
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Application.STATUS_CHOICES):
            application.status = new_status
            application.save()
            messages.success(request, "Application status updated successfully!")
    
    return redirect('dashboard:employer_dashboard')

@login_required
def edit_application(request, application_id):
    application = get_object_or_404(Application, id=application_id, job_seeker=request.user.jobseeker)
    
    if application.status != 'pending':
        messages.error(request, "You can only edit pending applications.")
        return redirect('dashboard:jobseeker_dashboard')
    
    if request.method == 'POST':
        application.cover_letter = request.POST.get('cover_letter')
        application.save()
        messages.success(request, "Application updated successfully!")
        return redirect('dashboard:jobseeker_dashboard')
    
    return redirect('dashboard:jobseeker_dashboard')

@login_required
def withdraw_application(request, application_id):
    if request.method == 'POST':
        application = get_object_or_404(Application, id=application_id, job_seeker=request.user.jobseeker)
        
        if application.status != 'pending':
            messages.error(request, "You can only withdraw pending applications.")
            return redirect('dashboard:jobseeker_dashboard')
        
        application.delete()
        messages.success(request, "Application withdrawn successfully!")
    
    return redirect('dashboard:jobseeker_dashboard')

@login_required
def clear_browse_history(request):
    """
    清除求职者的浏览历史
    """
    if not request.user.is_job_seeker:
        messages.error(request, "Access denied. Job seeker account required.")
        return redirect('jobs:home')
    
    if request.method == 'POST':
        try:
            JobBrowseHistory.objects.filter(job_seeker=request.user.jobseeker).delete()
            messages.success(request, "浏览历史已清除")
        except Exception as e:
            messages.error(request, "清除浏览历史时发生错误")
    
    return redirect('dashboard:jobseeker_dashboard')
