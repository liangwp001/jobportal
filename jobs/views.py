from django.shortcuts import render
from django.contrib import messages
from apps.jobs.models import JobInfo

def job_list(request):
    jobs = JobInfo.objects.filter(is_active=True)
    
    # Handle category filter
    category = request.GET.get('category')
    if category:
        jobs = jobs.filter(category=category)
        
        # If no jobs found for category
        if not jobs.exists():
            messages.info(request, "No jobs available in this category at the moment.")
            
    return render(request, 'jobs/job_list.html', {'jobs': jobs}) 