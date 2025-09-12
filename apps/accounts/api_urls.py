from django.urls import path
from . import api_views

app_name = 'accounts_api'

urlpatterns = [
    # 认证相关API
    path('login/', api_views.LoginAPIView.as_view(), name='login'),
    path('logout/', api_views.LogoutAPIView.as_view(), name='logout'),
    path('signup/', api_views.JobSeekerSignupAPIView.as_view(), name='signup'),
    
    # 邮箱验证API
    path('send-verification-code/', api_views.SendVerificationCodeAPIView.as_view(), name='send_verification_code'),
    path('verify-code/', api_views.VerifyCodeAPIView.as_view(), name='verify_code'),
    
    # 密码重置API
    path('send-password-reset-code/', api_views.SendPasswordResetCodeAPIView.as_view(), name='send_password_reset_code'),
    path('password-reset/', api_views.PasswordResetAPIView.as_view(), name='password_reset'),
    
    # 用户资料API
    path('profile/', api_views.UserProfileAPIView.as_view(), name='profile'),
    path('update-profile/', api_views.UpdateProfileAPIView.as_view(), name='update_profile'),
]


