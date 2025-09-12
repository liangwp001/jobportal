from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.home, name='home'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/post/', views.post_job, name='post_job'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('jobs/<int:job_id>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('job-posts/<int:job_post_id>/', views.job_post_detail, name='job_post_detail'),
    path('test-job-posts/', views.test_job_posts, name='test_job_posts'),
    path('categories/', views.categories, name='categories'),
    path('companies/', views.companies, name='companies'),
    path('companies/<int:pk>/', views.company_detail, name='company_detail'),
]