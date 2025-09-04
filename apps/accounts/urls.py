from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # 移除雇主注册路由 - 只保留求职者注册
    # path('signup/employer/', views.employer_signup, name='employer_signup'),
    path('signup/jobseeker/', views.jobseeker_signup, name='jobseeker_signup'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    # 移除雇主个人资料路由
    # path('employer/profile/', views.employer_profile, name='employer_profile'),
    # 邮箱验证相关路由
    path('send-verification-code/', views.send_verification_code, name='send_verification_code'),
    path('verify-code/', views.verify_code, name='verify_code'),
    # 密码重置相关路由
    path('password_reset/', views.password_reset_view, name='password_reset'),
    path('password_reset/confirm/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('password_reset/complete/', views.password_reset_complete_view, name='password_reset_complete'),
    path('send-password-reset-code/', views.send_password_reset_code, name='send_password_reset_code'),
]