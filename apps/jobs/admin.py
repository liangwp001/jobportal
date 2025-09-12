from django import forms
from django.contrib import admin
from .models import JobInfo, JobPost, Application

@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'category', 'publish_date', 'is_active')
    list_filter = ('is_active', 'category', 'publish_date')
    search_fields = ('title', 'organization')
    date_hierarchy = 'publish_date'

@admin.register(JobInfo)
class JobInfoAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'organization', 'category', 'job_location', 'employment_type', 'created_at', 'is_active')
    list_filter = ('is_active', 'category', 'employment_type', 'has_staffing_quota')
    search_fields = ('job_title', 'organization', 'job_location')
    date_hierarchy = 'created_at'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job_info', 'job_seeker', 'applied_date', 'status')
    list_filter = ('status', 'applied_date')
    search_fields = ('job_info__job_title', 'job_seeker__user__username')
    date_hierarchy = 'applied_date'