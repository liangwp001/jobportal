from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Employer, JobSeeker, EmailVerification
from .utils import create_or_update_verification, verify_email_code

class PasswordInputWithToggle(forms.PasswordInput):
    """自定义密码输入框，包含显示/隐藏切换按钮"""
    def __init__(self, attrs=None, render_value=False):
        default_attrs = {
            'class': 'w-full px-4 py-3 pr-12 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all hover:border-blue-400'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs, render_value)
    
    def render(self, name, value, attrs=None, renderer=None):
        widget_html = super().render(name, value, attrs, renderer)
        
        # 获取输入框的ID
        input_id = attrs.get('id', f'id_{name}')
        
        # 添加眼睛图标按钮
        toggle_button = f'''
        <div class="relative">
            {widget_html}
            <button type="button" 
                    class="password-toggle absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 transition-colors"
                    data-target="{input_id}">
                <!-- Eye icon (hidden) -->
                <svg class="eye-hidden h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                </svg>
                <!-- Eye slash icon (visible) -->
                <svg class="eye-visible h-5 w-5 hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"></path>
                </svg>
            </button>
        </div>
        '''
        
        return toggle_button

class EmployerSignUpForm(UserCreationForm):
    company_name = forms.CharField(max_length=255)
    company_description = forms.CharField(widget=forms.Textarea, required=False)
    company_website = forms.URLField(required=False)
    company_logo = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_employer = True
        if commit:
            user.save()
            Employer.objects.create(
                user=user,
                company_name=self.cleaned_data.get('company_name'),
                company_description=self.cleaned_data.get('company_description'),
                company_website=self.cleaned_data.get('company_website'),
                company_logo=self.cleaned_data.get('company_logo')
            )
        return user

class JobSeekerSignUpForm(UserCreationForm):
    skills = forms.CharField(widget=forms.Textarea, required=False)
    resume = forms.FileField(required=False)
    experience = forms.CharField(widget=forms.Textarea, required=False)
    education = forms.CharField(widget=forms.Textarea, required=False)
    verification_code = forms.CharField(max_length=6, required=True, label='验证码')

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # 检查邮箱是否已被验证
            try:
                verification = EmailVerification.objects.get(email=email)
                if not verification.is_verified:
                    raise forms.ValidationError("请先验证邮箱")
            except EmailVerification.DoesNotExist:
                raise forms.ValidationError("请先获取并验证邮箱验证码")
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code')
        email = self.cleaned_data.get('email')
        
        if verification_code and email:
            is_valid, message = verify_email_code(email, verification_code)
            if not is_valid:
                raise forms.ValidationError(message)
        
        return verification_code

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_job_seeker = True
        if commit:
            user.save()
            JobSeeker.objects.create(
                user=user,
                skills=self.cleaned_data.get('skills'),
                resume=self.cleaned_data.get('resume'),
                experience=self.cleaned_data.get('experience'),
                education=self.cleaned_data.get('education')
            )
        return user

class EmailVerificationForm(forms.Form):
    email = forms.EmailField(label='邮箱地址', max_length=254)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # 检查邮箱是否已被注册
            if CustomUser.objects.filter(email=email).exists():
                raise forms.ValidationError("该邮箱已被注册")
        return email

class PasswordResetEmailVerificationForm(forms.Form):
    """密码重置专用邮箱验证表单"""
    email = forms.EmailField(label='邮箱地址', max_length=254)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # 检查邮箱是否已注册
            if not CustomUser.objects.filter(email=email).exists():
                raise forms.ValidationError("该邮箱未注册，请检查邮箱地址是否正确")
        return email

class PasswordResetForm(forms.Form):
    """密码重置表单 - 第一步：输入邮箱"""
    email = forms.EmailField(
        label='邮箱地址', 
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all hover:border-blue-400',
            'placeholder': '请输入您的注册邮箱'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # 检查邮箱是否已注册
            if not CustomUser.objects.filter(email=email).exists():
                raise forms.ValidationError("该邮箱未注册，请检查邮箱地址是否正确")
        return email

class PasswordResetConfirmForm(forms.Form):
    """密码重置表单 - 第二步：验证码和新密码"""
    email = forms.EmailField(widget=forms.HiddenInput())
    verification_code = forms.CharField(
        label='验证码',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all hover:border-blue-400',
            'placeholder': '请输入6位验证码',
            'maxlength': '6'
        })
    )
    new_password1 = forms.CharField(
        label='新密码',
        widget=PasswordInputWithToggle(attrs={
            'placeholder': '请输入新密码'
        })
    )
    new_password2 = forms.CharField(
        label='确认新密码',
        widget=PasswordInputWithToggle(attrs={
            'placeholder': '请再次输入新密码'
        })
    )
    
    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code')
        email = self.cleaned_data.get('email')
        
        if verification_code and email:
            is_valid, message = verify_email_code(email, verification_code)
            if not is_valid:
                raise forms.ValidationError(message)
        
        return verification_code
    
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("两次输入的密码不一致")
            
            # 密码强度验证
            if len(password1) < 8:
                raise forms.ValidationError("密码长度至少8位")
            
            if not any(c.isupper() for c in password1):
                raise forms.ValidationError("密码必须包含至少一个大写字母")
            
            if not any(c.isdigit() for c in password1):
                raise forms.ValidationError("密码必须包含至少一个数字")
            
            if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password1):
                raise forms.ValidationError("密码必须包含至少一个特殊字符")
        
        return password2 

class ProfileEditForm(forms.ModelForm):
    """个人资料编辑表单"""
    first_name = forms.CharField(
        label='名字',
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all hover:border-blue-400',
            'placeholder': '请输入您的名字'
        })
    )
    last_name = forms.CharField(
        label='姓氏',
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all hover:border-blue-400',
            'placeholder': '请输入您的姓氏'
        })
    )
    email = forms.EmailField(
        label='邮箱地址',
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all hover:border-blue-400',
            'placeholder': '请输入您的邮箱地址'
        })
    )
    skills = forms.CharField(
        label='技能',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all hover:border-blue-400',
            'placeholder': '请输入您的技能，用逗号分隔',
            'rows': 3
        }),
        help_text='请输入您的技能，用逗号分隔，例如：Python, Django, JavaScript'
    )
    experience = forms.CharField(
        label='工作经验',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all hover:border-blue-400',
            'placeholder': '请描述您的工作经验',
            'rows': 5
        })
    )
    education = forms.CharField(
        label='教育背景',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all hover:border-blue-400',
            'placeholder': '请描述您的教育背景',
            'rows': 4
        })
    )
    resume = forms.FileField(
        label='简历文件',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all hover:border-blue-400',
            'accept': '.pdf,.doc,.docx'
        }),
        help_text='支持PDF、DOC、DOCX格式，文件大小不超过10MB'
    )

    class Meta:
        model = JobSeeker
        fields = ['skills', 'experience', 'education', 'resume']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # 如果传入了用户对象，初始化用户相关字段
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and self.user:
            # 检查邮箱是否已被其他用户使用
            if CustomUser.objects.filter(email=email).exclude(id=self.user.id).exists():
                raise forms.ValidationError("该邮箱已被其他用户使用")
        return email

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            # 检查文件大小（10MB限制）
            if resume.size > 10 * 1024 * 1024:
                raise forms.ValidationError("文件大小不能超过10MB")
            
            # 检查文件类型
            allowed_types = ['application/pdf', 'application/msword', 
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            if resume.content_type not in allowed_types:
                raise forms.ValidationError("只支持PDF、DOC、DOCX格式的文件")
        
        return resume

    def save(self, commit=True):
        jobseeker = super().save(commit=False)
        
        # 更新用户基本信息
        if self.user:
            self.user.first_name = self.cleaned_data.get('first_name', '')
            self.user.last_name = self.cleaned_data.get('last_name', '')
            self.user.email = self.cleaned_data.get('email', '')
            if commit:
                self.user.save()
        
        if commit:
            jobseeker.save()
        
        return jobseeker