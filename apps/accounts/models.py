from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
import random
import string
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    is_employer = models.BooleanField(default=False)
    is_job_seeker = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Employer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    company_description = models.TextField(blank=True)
    company_website = models.URLField(blank=True)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True)
    location = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.company_name

    def get_absolute_url(self):
        return reverse('accounts:employer_profile', args=[str(self.id)])

    @property
    def job_count(self):
        return self.jobs.filter(is_active=True).count()

class JobSeeker(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/', blank=True)
    skills = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    education = models.TextField(blank=True)
    
    def __str__(self):
        return self.user.username

class EmailVerification(models.Model):
    email = models.EmailField(unique=True)
    verification_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "邮箱验证"
        verbose_name_plural = "邮箱验证"
    
    def __str__(self):
        return f"{self.email} - {self.verification_code}"
    
    @classmethod
    def generate_code(cls):
        """生成6位数字验证码"""
        return ''.join(random.choices(string.digits, k=6))
    
    def is_expired(self):
        """检查验证码是否过期（10分钟）"""
        return timezone.now() > self.created_at + timedelta(minutes=10)
    
    def can_resend(self):
        """检查是否可以重新发送验证码（1分钟间隔）"""
        return timezone.now() > self.created_at + timedelta(minutes=1)
    
    def increment_attempts(self):
        """增加尝试次数"""
        self.attempts += 1
        self.save(update_fields=['attempts'])
    
    def is_max_attempts_reached(self):
        """检查是否达到最大尝试次数（5次）"""
        return self.attempts >= 5

class EmailSendRateLimit(models.Model):
    """邮箱验证码发送频率限制"""
    email = models.EmailField()
    sent_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "邮箱发送频率限制"
        verbose_name_plural = "邮箱发送频率限制"
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.email} - {self.sent_at}"
    
    @classmethod
    def can_send_email(cls, email, ip_address=None, time_window_minutes=1, max_emails=10):
        """
        检查是否可以发送邮件
        
        Args:
            email: 邮箱地址
            ip_address: IP地址（可选）
            time_window_minutes: 时间窗口（分钟）
            max_emails: 最大邮件数量
            
        Returns:
            tuple: (can_send: bool, remaining_time: int, message: str)
        """
        from django.utils import timezone
        from datetime import timedelta
        
        # 计算时间窗口
        time_threshold = timezone.now() - timedelta(minutes=time_window_minutes)
        
        # 查询该邮箱在时间窗口内的发送记录
        recent_sends = cls.objects.filter(
            email=email,
            sent_at__gte=time_threshold
        )
        
        # 如果提供了IP地址，也检查IP限制
        if ip_address:
            ip_recent_sends = cls.objects.filter(
                ip_address=ip_address,
                sent_at__gte=time_threshold
            )
            if ip_recent_sends.count() >= max_emails:
                # 计算剩余时间
                oldest_send = ip_recent_sends.order_by('sent_at').first()
                if oldest_send:
                    remaining_seconds = int((oldest_send.sent_at + timedelta(minutes=time_window_minutes) - timezone.now()).total_seconds())
                    return False, remaining_seconds, f"IP地址发送过于频繁，请等待 {remaining_seconds} 秒后重试"
        
        # 检查邮箱发送频率
        email_count = recent_sends.count()
        if email_count >= max_emails:
            # 计算剩余时间
            oldest_send = recent_sends.order_by('sent_at').first()
            if oldest_send:
                remaining_seconds = int((oldest_send.sent_at + timedelta(minutes=time_window_minutes) - timezone.now()).total_seconds())
                return False, remaining_seconds, f"该邮箱发送过于频繁，请等待 {remaining_seconds} 秒后重试"
        
        return True, 0, "可以发送"
    
    @classmethod
    def record_email_send(cls, email, ip_address=None, user_agent=''):
        """记录邮件发送"""
        return cls.objects.create(
            email=email,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @classmethod
    def cleanup_old_records(cls, days=7):
        """清理旧的发送记录"""
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count, _ = cls.objects.filter(sent_at__lt=cutoff_date).delete()
        return deleted_count
