from django.db import models
from apps.accounts.models import Employer, JobSeeker

class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class (e.g., 'fas fa-code')")
    
    def __str__(self):
        return self.name
    
    @property
    def job_count(self):
        return self.job_set.filter(is_active=True).count()

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    ]

    title = models.CharField(max_length=200)
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name='jobs')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    requirements = models.TextField()
    location = models.CharField(max_length=100)
    salary = models.CharField(max_length=100)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    posted_date = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-posted_date']

    def __str__(self):
        return self.title

class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewing', 'Reviewing'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job', 'job_seeker')

    def __str__(self):
        return f"{self.job_seeker.user.username} - {self.job.title}"

class JobBookmark(models.Model):
    """
    Model to handle job bookmarks/favorites for job seekers
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='bookmarks')
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, related_name='bookmarks')
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'job_seeker')
        ordering = ['-created_date']

    def __str__(self):
        return f"{self.job_seeker.user.username} - {self.job.title} (收藏)"

class JobBrowseHistory(models.Model):
    """
    Model to track job browsing history for job seekers
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='browse_history')
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, related_name='browse_history')
    browsed_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-browsed_date']
        indexes = [
            models.Index(fields=['job_seeker', '-browsed_date']),
        ]

    def __str__(self):
        return f"{self.job_seeker.user.username} - {self.job.title} (浏览于 {self.browsed_date.strftime('%Y-%m-%d %H:%M')})"
