import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import EmailVerification, EmailSendRateLimit

logger = logging.getLogger(__name__)

def send_verification_email(email, verification_code):
    """
    发送邮箱验证码
    """
    try:
        subject = '考编AI - 邮箱验证码'
        
        # 创建邮件内容
        context = {
            'verification_code': verification_code,
            'email': email,
        }
        
        # 渲染邮件模板
        html_message = render_to_string('accounts/verification_email.html', context)
        
        # 发送邮件
        send_mail(
            subject=subject,
            message=f'您的验证码是：{verification_code}，请在10分钟内使用。',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"验证码邮件发送成功: {email}")
        return True
        
    except Exception as e:
        logger.error(f"验证码邮件发送失败: {email}, 错误: {str(e)}")
        return False

def create_or_update_verification(email, ip_address=None, user_agent=''):
    """
    创建或更新邮箱验证记录（带频率限制）
    """
    try:
        # 检查频率限制
        can_send, remaining_time, message = EmailSendRateLimit.can_send_email(
            email=email,
            ip_address=ip_address,
            time_window_minutes=1,  # 1分钟时间窗口
            max_emails=10  # 最多10封邮件
        )
        
        if not can_send:
            logger.warning(f"频率限制触发: {email}, IP: {ip_address}, 消息: {message}")
            return None, message
        
        # 生成验证码
        verification_code = EmailVerification.generate_code()
        
        # 创建或更新验证记录
        verification, created = EmailVerification.objects.update_or_create(
            email=email,
            defaults={
                'verification_code': verification_code,
                'is_verified': False,
                'attempts': 0,
            }
        )
        
        # 发送验证码邮件
        if send_verification_email(email, verification_code):
            # 记录发送历史
            EmailSendRateLimit.record_email_send(
                email=email,
                ip_address=ip_address,
                user_agent=user_agent
            )
            logger.info(f"验证码发送成功: {email}, IP: {ip_address}")
            return verification, "验证码发送成功"
        else:
            return None, "验证码发送失败"
            
    except Exception as e:
        logger.error(f"创建验证记录失败: {email}, 错误: {str(e)}")
        return None, "验证码发送失败，请稍后重试"

def verify_email_code(email, code):
    """
    验证邮箱验证码
    """
    try:
        verification = EmailVerification.objects.get(email=email)
        
        # 检查是否过期
        if verification.is_expired():
            return False, "验证码已过期，请重新获取"
        
        # 检查是否达到最大尝试次数
        if verification.is_max_attempts_reached():
            return False, "验证失败次数过多，请重新获取验证码"
        
        # 验证码是否正确
        if verification.verification_code == code:
            verification.is_verified = True
            verification.save()
            return True, "验证成功"
        else:
            # 增加尝试次数
            verification.increment_attempts()
            remaining_attempts = settings.VERIFICATION_MAX_ATTEMPTS - verification.attempts
            return False, f"验证码错误，还有{remaining_attempts}次机会"
            
    except EmailVerification.DoesNotExist:
        return False, "验证码不存在，请重新获取"
    except Exception as e:
        logger.error(f"验证邮箱验证码失败: {email}, 错误: {str(e)}")
        return False, "验证失败，请稍后重试"
