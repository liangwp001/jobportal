from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging

from .forms import EmployerSignUpForm, JobSeekerSignUpForm, EmailVerificationForm, PasswordResetForm, PasswordResetConfirmForm, PasswordResetEmailVerificationForm, ProfileEditForm
from .models import CustomUser, JobSeeker, Employer, EmailVerification
from .utils import create_or_update_verification, verify_email_code
from apps.jobs.models import Application

logger = logging.getLogger(__name__)

def get_client_ip(request):
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(View):
    """登录API"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            username_or_email = data.get('username_or_email')
            password = data.get('password')
            user_type = data.get('user_type', 'job_seeker')

            if not username_or_email or not password:
                return JsonResponse({
                    'success': False,
                    'message': '用户名/邮箱和密码不能为空'
                }, status=400)

            try:
                user = CustomUser.objects.get(
                    Q(username=username_or_email) | Q(email=username_or_email)
                )
                
                # 只允许求职者登录
                if not user.is_job_seeker:
                    return JsonResponse({
                        'success': False,
                        'message': '抱歉，此平台仅支持求职者登录。'
                    }, status=400)

                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    return JsonResponse({
                        'success': True,
                        'message': f'欢迎回来，{user.username}！',
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'is_job_seeker': user.is_job_seeker,
                        }
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': '密码错误。'
                    }, status=400)
            except CustomUser.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': '未找到使用这些凭据的账户。'
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': '无效的JSON数据'
            }, status=400)
        except Exception as e:
            logger.error(f"登录API错误: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': '服务器内部错误'
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class LogoutAPIView(View):
    """登出API"""
    
    def post(self, request):
        try:
            logout(request)
            return JsonResponse({
                'success': True,
                'message': '已成功登出'
            })
        except Exception as e:
            logger.error(f"登出API错误: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': '服务器内部错误'
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class SendVerificationCodeAPIView(View):
    """发送邮箱验证码API"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            if not email:
                return JsonResponse({
                    'success': False,
                    'message': '邮箱地址不能为空'
                }, status=400)

            # 检查邮箱是否已被注册
            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'message': '该邮箱已被注册'
                }, status=400)

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
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': '无效的JSON数据'
            }, status=400)
        except Exception as e:
            logger.error(f"发送验证码API错误: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': '服务器内部错误'
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class VerifyCodeAPIView(View):
    """验证邮箱验证码API"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            code = data.get('code')
            
            if not email or not code:
                return JsonResponse({
                    'success': False,
                    'message': '邮箱和验证码不能为空'
                }, status=400)
            
            is_valid, message = verify_email_code(email, code)
            
            return JsonResponse({
                'success': is_valid,
                'message': message
            })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': '无效的JSON数据'
            }, status=400)
        except Exception as e:
            logger.error(f"验证码API错误: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': '服务器内部错误'
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class JobSeekerSignupAPIView(View):
    """求职者注册API"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # 验证必填字段
            required_fields = ['username', 'email', 'password1', 'password2', 'verification_code']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        'success': False,
                        'message': f'{field} 不能为空'
                    }, status=400)

            # 验证密码是否匹配
            if data['password1'] != data['password2']:
                return JsonResponse({
                    'success': False,
                    'message': '两次输入的密码不一致'
                }, status=400)

            # 验证邮箱验证码
            email = data['email']
            code = data['verification_code']
            is_valid, message = verify_email_code(email, code)
            if not is_valid:
                return JsonResponse({
                    'success': False,
                    'message': message
                }, status=400)

            # 检查用户名是否已存在
            if CustomUser.objects.filter(username=data['username']).exists():
                return JsonResponse({
                    'success': False,
                    'message': '用户名已存在'
                }, status=400)

            # 检查邮箱是否已存在
            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'message': '邮箱已被注册'
                }, status=400)

            # 创建用户
            user = CustomUser.objects.create_user(
                username=data['username'],
                email=email,
                password=data['password1'],
                is_job_seeker=True
            )

            # 创建求职者档案
            JobSeeker.objects.create(
                user=user,
                skills=data.get('skills', ''),
                experience=data.get('experience', ''),
                education=data.get('education', '')
            )

            # 自动登录
            login(request, user)

            return JsonResponse({
                'success': True,
                'message': '欢迎！您的求职者账户已创建成功。',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_job_seeker': user.is_job_seeker,
                }
            })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': '无效的JSON数据'
            }, status=400)
        except Exception as e:
            logger.error(f"注册API错误: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': '服务器内部错误'
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class SendPasswordResetCodeAPIView(View):
    """发送密码重置验证码API"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            if not email:
                return JsonResponse({
                    'success': False,
                    'message': '邮箱地址不能为空'
                }, status=400)

            # 检查邮箱是否已注册
            if not CustomUser.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'message': '该邮箱未注册，请检查邮箱地址是否正确'
                }, status=400)

            # 获取客户端信息
            ip_address = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # 创建或更新验证记录（带频率限制）
            verification, message = create_or_update_verification(email, ip_address, user_agent)
            
            if verification:
                # 将邮箱存储到session中，用于下一步
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
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': '无效的JSON数据'
            }, status=400)
        except Exception as e:
            logger.error(f"发送密码重置验证码API错误: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': '服务器内部错误'
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetAPIView(View):
    """密码重置API"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')
            verification_code = data.get('verification_code')
            new_password1 = data.get('new_password1')
            new_password2 = data.get('new_password2')
            
            if not all([email, verification_code, new_password1, new_password2]):
                return JsonResponse({
                    'success': False,
                    'message': '所有字段都不能为空'
                }, status=400)

            # 验证密码是否匹配
            if new_password1 != new_password2:
                return JsonResponse({
                    'success': False,
                    'message': '两次输入的密码不一致'
                }, status=400)

            # 验证邮箱验证码
            is_valid, message = verify_email_code(email, verification_code)
            if not is_valid:
                return JsonResponse({
                    'success': False,
                    'message': message
                }, status=400)

            try:
                # 获取用户
                user = CustomUser.objects.get(email=email)
                
                # 更新密码
                user.password = make_password(new_password1)
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
                return JsonResponse({
                    'success': True,
                    'message': '密码重置成功！请使用新密码登录。'
                })
                
            except CustomUser.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': '用户不存在'
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': '无效的JSON数据'
            }, status=400)
        except Exception as e:
            logger.error(f"密码重置API错误: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': '服务器内部错误'
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class UserProfileAPIView(View):
    """获取用户信息API"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': '用户未登录'
            }, status=401)

        try:
            user = request.user
            jobseeker = None
            
            if user.is_job_seeker:
                try:
                    jobseeker = user.jobseeker
                except JobSeeker.DoesNotExist:
                    jobseeker = JobSeeker.objects.create(user=user)

            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_job_seeker': user.is_job_seeker,
                    'is_employer': user.is_employer,
                    'jobseeker': {
                        'skills': jobseeker.skills if jobseeker else '',
                        'experience': jobseeker.experience if jobseeker else '',
                        'education': jobseeker.education if jobseeker else '',
                        'resume': jobseeker.resume.url if jobseeker and jobseeker.resume else None,
                    } if jobseeker else None
                }
            })
        except Exception as e:
            logger.error(f"获取用户信息API错误: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': '服务器内部错误'
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class UpdateProfileAPIView(View):
    """更新用户资料API"""
    
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': '用户未登录'
            }, status=401)

        if not request.user.is_job_seeker:
            return JsonResponse({
                'success': False,
                'message': '只有求职者可以编辑个人资料'
            }, status=403)

        try:
            data = json.loads(request.body)
            
            # 更新用户基本信息
            user = request.user
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'email' in data:
                # 检查邮箱是否已被其他用户使用
                if CustomUser.objects.filter(email=data['email']).exclude(id=user.id).exists():
                    return JsonResponse({
                        'success': False,
                        'message': '该邮箱已被其他用户使用'
                    }, status=400)
                user.email = data['email']
            
            user.save()

            # 更新求职者档案
            try:
                jobseeker = user.jobseeker
            except JobSeeker.DoesNotExist:
                jobseeker = JobSeeker.objects.create(user=user)

            if 'skills' in data:
                jobseeker.skills = data['skills']
            if 'experience' in data:
                jobseeker.experience = data['experience']
            if 'education' in data:
                jobseeker.education = data['education']
            
            jobseeker.save()

            return JsonResponse({
                'success': True,
                'message': '个人资料更新成功！',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_job_seeker': user.is_job_seeker,
                    'jobseeker': {
                        'skills': jobseeker.skills,
                        'experience': jobseeker.experience,
                        'education': jobseeker.education,
                        'resume': jobseeker.resume.url if jobseeker.resume else None,
                    }
                }
            })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': '无效的JSON数据'
            }, status=400)
        except Exception as e:
            logger.error(f"更新资料API错误: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': '服务器内部错误'
            }, status=500)


