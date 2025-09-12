from django.db import models
from apps.accounts.models import Employer, JobSeeker
from enum import Enum


# 枚举类型定义
class PublicInstitutionJobCategory(str, Enum):
    MANAGEMENT = "管理岗位"
    PROFESSIONAL_TECH = "专业技术岗位"
    SUPPORT_SKILL = "工勤技能岗位"


class DegreeLevel(str, Enum):
    NONE = "不限"
    PRIMARY = "小学"
    JUNIOR = "初中"
    SENIOR = "高中（含中专、技校、职高）"
    COLLEGE = "大专（含高职、高专）"
    BACHELOR = "本科"
    MASTER = "硕士"
    DOCTOR = "博士"


class AgeLevel(str, Enum):
    NONE = "不限"
    AGE_25 = "25岁以下"
    AGE_30 = "30岁以下"
    AGE_35 = "35岁以下"
    AGE_40 = "40岁以下"
    AGE_45 = "45岁以下"
    AGE_50 = "50岁以下"
    AGE_55 = "55岁以下"
    AGE_60 = "60岁以下"
    AGE_65 = "65岁以下"


class JobExperienceLevel(str, Enum):
    NONE = "不限"
    NEW_GRAD = "应届生"
    Y_1 = "1年以上"
    Y_3 = "3年以上"
    Y_5 = "5年以上"
    Y_10 = "10年以上"


class JobPostCategory(str, Enum):
    CIVIL_SERVANT = "公务员"
    PUBLIC_INSTITUTION = "事业单位"
    TEACHER = "教师招聘"
    MEDICAL = "医疗招聘"
    BANK = "银行招聘"
    SOE = "国企招聘"
    THREE_SUPPORTS = "三支一扶"
    POLICE = "招警"
    SELECTION = "选调生"
    COLLEGE_VILLAGE = "大学生村官"
    PUBLIC_SELECTION = "公选遴选"
    GRASSROOTS = "基层工作者"
    ARMY_CIVILIAN = "军队文职"
    PUBLIC_WELFARE = "公益性岗位"


class JobPost(models.Model):
    """招聘公告模型"""
    title = models.CharField(max_length=200, verbose_name="招聘公告标题")
    source_url = models.CharField(max_length=512, verbose_name="招聘公告详情链接", blank=True, null=True)
    html_text = models.TextField(null=True, blank=True, verbose_name="招聘公告正文(html文本)")
    publish_date = models.DateField(null=True, blank=True, verbose_name="公告发布时间")
    organization = models.CharField(max_length=200, null=True, blank=True, verbose_name="招聘单位名称")
    application_start_date = models.DateField(null=True, blank=True, verbose_name="报名开始时间")
    application_end_date = models.DateField(null=True, blank=True, verbose_name="报名截止时间")
    category = models.CharField(
        max_length=50,
        choices=[(tag.value, tag.value) for tag in JobPostCategory],
        null=True,
        blank=True,
        verbose_name="招聘分类"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_active = models.BooleanField(default=True, verbose_name="是否有效")

    class Meta:
        ordering = ['-publish_date', '-created_at']
        verbose_name = "招聘公告"
        verbose_name_plural = "招聘公告"

    def __str__(self):
        return self.title


class JobInfo(models.Model):
    """岗位信息模型"""
    # 基本信息
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='jobs', verbose_name="所属招聘公告")
    organization = models.CharField(max_length=200, null=True, blank=True, verbose_name="招聘单位名称")
    job_title = models.CharField(max_length=200, null=True, blank=True, verbose_name="岗位名称")
    employment_type = models.CharField(max_length=100, null=True, blank=True, verbose_name="用工方式")
    has_staffing_quota = models.BooleanField(null=True, blank=True, verbose_name="是否属于正式人员编制")
    category = models.CharField(
        max_length=50,
        choices=[(tag.value, tag.value) for tag in PublicInstitutionJobCategory],
        null=True,
        blank=True,
        verbose_name="岗位类别"
    )
    job_location = models.CharField(max_length=200, null=True, blank=True, verbose_name="工作地点")
    num_positions = models.CharField(max_length=50, null=True, blank=True, verbose_name="招聘人数")
    is_targeted_recruitment = models.BooleanField(null=True, blank=True, verbose_name="是否是定向招聘")
    targeted_recruitment_scope = models.TextField(null=True, blank=True, verbose_name="定向招聘范围")
    registration_methods = models.CharField(max_length=200, null=True, blank=True, verbose_name="报名方式")
    registration_materials = models.TextField(null=True, blank=True, verbose_name="报名所需材料")
    contacts = models.CharField(max_length=100, null=True, blank=True, verbose_name="联系人")
    contact_methods = models.CharField(max_length=200, null=True, blank=True, verbose_name="联系方式")

    # 任职要求
    job_experience_requirement = models.TextField(null=True, blank=True, verbose_name="工作经验要求")
    min_job_experience_level = models.CharField(
        max_length=20,
        choices=[(tag.value, tag.value) for tag in JobExperienceLevel],
        default=JobExperienceLevel.NONE.value,
        verbose_name="最低工作经验要求"
    )
    degree_requirement = models.TextField(null=True, blank=True, verbose_name="学历要求")
    min_degree_level = models.CharField(
        max_length=20,
        choices=[(tag.value, tag.value) for tag in DegreeLevel],
        default=DegreeLevel.NONE.value,
        verbose_name="最低学历要求"
    )
    major_requirement = models.TextField(null=True, blank=True, verbose_name="专业要求")
    age_requirement = models.CharField(max_length=100, null=True, blank=True, verbose_name="年龄要求")
    max_age_level = models.CharField(
        max_length=20,
        choices=[(tag.value, tag.value) for tag in AgeLevel],
        default=AgeLevel.NONE.value,
        verbose_name="年龄上限要求"
    )
    graduation_status_requirement = models.CharField(max_length=100, null=True, blank=True, verbose_name="毕业时间/应届身份要求")
    title_requirement = models.CharField(max_length=100, null=True, blank=True, verbose_name="职称要求")
    job_skill_requirements = models.TextField(null=True, blank=True, verbose_name="工作技能要求")
    political_status_requirement = models.CharField(max_length=100, null=True, blank=True, verbose_name="政治面貌要求")
    certificate_requirement = models.TextField(null=True, blank=True, verbose_name="证书要求")
    minimum_service_years_requirement = models.CharField(max_length=100, null=True, blank=True, verbose_name="最低服务年限要求")
    gender_requirement = models.CharField(max_length=50, null=True, blank=True, verbose_name="性别要求")
    other_requirement = models.TextField(null=True, blank=True, verbose_name="其他要求")

    # 岗位职责和待遇
    job_responsibilities = models.TextField(null=True, blank=True, verbose_name="岗位职责")
    salary_and_benefits = models.TextField(null=True, blank=True, verbose_name="薪资待遇")

    # 系统字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_active = models.BooleanField(default=True, verbose_name="是否有效")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "岗位信息"
        verbose_name_plural = "岗位信息"

    def __str__(self):
        return self.job_title or f"岗位-{self.id}"


class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewing', 'Reviewing'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    job_info = models.ForeignKey(JobInfo, on_delete=models.CASCADE, related_name='applications')
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job_info', 'job_seeker')

    def __str__(self):
        return f"{self.job_seeker.user.username} - {self.job_info.job_title}"


class JobBookmark(models.Model):
    """
    Model to handle job bookmarks/favorites for job seekers
    """
    job_info = models.ForeignKey(JobInfo, on_delete=models.CASCADE, related_name='bookmarks')
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, related_name='bookmarks')
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job_info', 'job_seeker')
        ordering = ['-created_date']

    def __str__(self):
        return f"{self.job_seeker.user.username} - {self.job_info.job_title} (收藏)"


class JobBrowseHistory(models.Model):
    """
    Model to track job browsing history for job seekers
    """
    job_info = models.ForeignKey(JobInfo, on_delete=models.CASCADE, related_name='browse_history')
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
        return f"{self.job_seeker.user.username} - {self.job_info.job_title} (浏览于 {self.browsed_date.strftime('%Y-%m-%d %H:%M')})"
