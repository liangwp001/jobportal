from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import make_password
from .forms import EmployerSignUpForm, JobSeekerSignUpForm, EmailVerificationForm, PasswordResetForm, PasswordResetConfirmForm, PasswordResetEmailVerificationForm
from .models import CustomUser, JobSeeker, Employer, EmailVerification
from .utils import create_or_update_verification, verify_email_code
from .forms import ProfileEditForm
from apps.jobs.models import Application
import logging

logger = logging.getLogger(__name__)

def get_client_ip(request):
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

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
            
            # 只允许求职者登录
            if not user.is_job_seeker:
                messages.error(request, "抱歉，此平台仅支持求职者登录。")
                return render(request, 'accounts/login.html')

            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"欢迎回来，{user.username}！")
                return redirect('dashboard:jobseeker_dashboard')
            else:
                messages.error(request, "密码错误。")
        except CustomUser.DoesNotExist:
            messages.error(request, "未找到使用这些凭据的账户。")
    
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
            messages.success(request, '欢迎！您的求职者账户已创建成功。')
            return redirect('dashboard:jobseeker_dashboard')
    else:
        form = JobSeekerSignUpForm()
    return render(request, 'accounts/signup_jobseeker.html', {'form': form})

@require_http_methods(["POST"])
def send_verification_code(request):
    """发送邮箱验证码"""
    form = EmailVerificationForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        
        # 获取客户端信息
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 创建或更新验证记录（带频率限制）
        verification, message = create_or_update_verification(email, ip_address, user_agent)
        
        if verification:
            return JsonResponse({
                'success': True,
                'message': f'验证码已发送到 {email}，请查收您的邮箱。'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': message
            })
    else:
        return JsonResponse({
            'success': False,
            'message': form.errors['email'][0] if 'email' in form.errors else '邮箱格式不正确'
        })

@require_http_methods(["POST"])
def verify_code(request):
    """验证邮箱验证码"""
    email = request.POST.get('email')
    code = request.POST.get('code')
    
    if not email or not code:
        return JsonResponse({
            'success': False,
            'message': '邮箱和验证码不能为空'
        })
    
    is_valid, message = verify_email_code(email, code)
    
    return JsonResponse({
        'success': is_valid,
        'message': message
    })

def signup_view(request):
    # 直接重定向到求职者注册页面，不再显示选择页面
    return redirect('accounts:jobseeker_signup')

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

def password_reset_view(request):
    """密码重置第一步：输入邮箱"""
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # 检查是否已经通过AJAX发送过验证码
            if 'verification_sent' in request.session and request.session.get('reset_email') == email:
                # 已经发送过验证码，直接跳转到下一步
                messages.success(request, f'验证码已发送到 {email}，请查收您的邮箱。')
                return redirect('accounts:password_reset_confirm')
            else:
                # 获取客户端信息
                ip_address = get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                
                # 创建或更新验证记录（带频率限制）
                verification, message = create_or_update_verification(email, ip_address, user_agent)
                
                if verification:
                    # 将邮箱存储到session中，用于下一步
                    request.session['reset_email'] = email
                    request.session['verification_sent'] = True
                    messages.success(request, f'验证码已发送到 {email}，请查收您的邮箱。')
                    return redirect('accounts:password_reset_confirm')
                else:
                    messages.error(request, message)
    else:
        form = PasswordResetForm()
    
    return render(request, 'accounts/password_reset.html', {'form': form})

def password_reset_confirm_view(request):
    """密码重置第二步：验证码和新密码"""
    # 检查是否有邮箱在session中
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, '请先输入邮箱地址。')
        return redirect('accounts:password_reset')
    
    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        form.fields['email'].initial = email  # 设置隐藏字段的值
        
        if form.is_valid():
            try:
                # 获取用户
                user = CustomUser.objects.get(email=email)
                
                # 更新密码
                new_password = form.cleaned_data['new_password1']
                user.password = make_password(new_password)
                user.save()
                
                # 清除session
                if 'reset_email' in request.session:
                    del request.session['reset_email']
                if 'verification_sent' in request.session:
                    del request.session['verification_sent']
                
                # 清除验证记录
                try:
                    verification = EmailVerification.objects.get(email=email)
                    verification.delete()
                except EmailVerification.DoesNotExist:
                    pass
                
                logger.info(f"密码重置成功: {email}")
                messages.success(request, '密码重置成功！请使用新密码登录。')
                return redirect('accounts:password_reset_complete')
                
            except CustomUser.DoesNotExist:
                messages.error(request, '用户不存在。')
                return redirect('accounts:password_reset')
            except Exception as e:
                logger.error(f"密码重置失败: {email}, 错误: {str(e)}")
                messages.error(request, '密码重置失败，请稍后重试。')
    else:
        form = PasswordResetConfirmForm()
        form.fields['email'].initial = email
    
    return render(request, 'accounts/password_reset_confirm.html', {
        'form': form, 
        'email': email
    })

def password_reset_complete_view(request):
    """密码重置完成页面"""
    return render(request, 'accounts/password_reset_complete.html')

@require_http_methods(["POST"])
def send_password_reset_code(request):
    """发送密码重置验证码"""
    form = PasswordResetEmailVerificationForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        
        # 获取客户端信息
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 创建或更新验证记录（带频率限制）
        verification, message = create_or_update_verification(email, ip_address, user_agent)
        
        if verification:
            # 设置session标记，避免重复发送
            request.session['reset_email'] = email
            request.session['verification_sent'] = True
            
            return JsonResponse({
                'success': True,
                'message': f'验证码已发送到 {email}，请查收您的邮箱。'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': message
            })
    else:
        return JsonResponse({
            'success': False,
            'message': form.errors['email'][0] if 'email' in form.errors else '邮箱格式不正确'
        })