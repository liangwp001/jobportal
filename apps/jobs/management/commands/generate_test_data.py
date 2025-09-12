from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from apps.jobs.models import JobPost, JobInfo, JobPostCategory, PublicInstitutionJobCategory, DegreeLevel, JobExperienceLevel, AgeLevel
import random

class Command(BaseCommand):
    help = '生成测试数据用于招聘平台'

    def add_arguments(self, parser):
        parser.add_argument(
            '--job-posts',
            type=int,
            default=10,
            help='要生成的招聘公告数量 (默认: 10)'
        )
        parser.add_argument(
            '--jobs-per-post',
            type=int,
            default=5,
            help='每个招聘公告的岗位数量 (默认: 5)'
        )

    def handle(self, *args, **options):
        job_posts_count = options['job_posts']
        jobs_per_post = options['jobs_per_post']
        
        self.stdout.write(f'开始生成 {job_posts_count} 个招聘公告，每个包含 {jobs_per_post} 个岗位...')
        
        # 清空现有数据
        JobInfo.objects.all().delete()
        JobPost.objects.all().delete()
        
        # 招聘公告数据模板
        job_post_templates = [
            {
                'title': '2024年公务员招录公告',
                'category': JobPostCategory.CIVIL_SERVANT.value,
                'organization': '某市人力资源和社会保障局',
            },
            {
                'title': '2024年事业单位公开招聘公告',
                'category': JobPostCategory.PUBLIC_INSTITUTION.value,
                'organization': '某市教育局',
            },
            {
                'title': '2024年教师招聘公告',
                'category': JobPostCategory.TEACHER.value,
                'organization': '某县教育局',
            },
            {
                'title': '2024年医疗系统招聘公告',
                'category': JobPostCategory.MEDICAL.value,
                'organization': '某市卫生健康委员会',
            },
            {
                'title': '2024年银行招聘公告',
                'category': JobPostCategory.BANK.value,
                'organization': '某银行股份有限公司',
            },
            {
                'title': '2024年国企招聘公告',
                'category': JobPostCategory.SOE.value,
                'organization': '某国有企业集团',
            },
            {
                'title': '2024年三支一扶招募公告',
                'category': JobPostCategory.THREE_SUPPORTS.value,
                'organization': '某省人力资源和社会保障厅',
            },
            {
                'title': '2024年招警公告',
                'category': JobPostCategory.POLICE.value,
                'organization': '某市公安局',
            },
            {
                'title': '2024年选调生招录公告',
                'category': JobPostCategory.SELECTION.value,
                'organization': '某省委组织部',
            },
            {
                'title': '2024年军队文职招聘公告',
                'category': JobPostCategory.ARMY_CIVILIAN.value,
                'organization': '某军区政治工作部',
            },
        ]
        
        # 岗位数据模板
        job_templates = [
            {
                'job_title': '综合管理岗',
                'category': PublicInstitutionJobCategory.MANAGEMENT.value,
                'employment_type': '正式编制',
                'job_location': '某市市区',
                'num_positions': '2',
                'degree_requirement': '本科及以上学历',
                'major_requirement': '行政管理、公共管理、法学等相关专业',
                'age_requirement': '35周岁以下',
                'job_responsibilities': '负责综合管理工作，包括文件起草、会议组织、协调各部门工作等。',
                'salary_and_benefits': '月薪5000-8000元，享受五险一金、带薪年假等福利待遇。',
            },
            {
                'job_title': '专业技术岗',
                'category': PublicInstitutionJobCategory.PROFESSIONAL_TECH.value,
                'employment_type': '正式编制',
                'job_location': '某市市区',
                'num_positions': '3',
                'degree_requirement': '本科及以上学历',
                'major_requirement': '计算机科学与技术、软件工程、信息管理等专业',
                'age_requirement': '30周岁以下',
                'job_responsibilities': '负责信息系统维护、数据分析、技术支持等工作。',
                'salary_and_benefits': '月薪6000-10000元，享受五险一金、绩效奖金等福利待遇。',
            },
            {
                'job_title': '工勤技能岗',
                'category': PublicInstitutionJobCategory.SUPPORT_SKILL.value,
                'employment_type': '合同制',
                'job_location': '某县县城',
                'num_positions': '1',
                'degree_requirement': '高中及以上学历',
                'major_requirement': '不限专业',
                'age_requirement': '40周岁以下',
                'job_responsibilities': '负责设备维护、后勤保障、安全保卫等工作。',
                'salary_and_benefits': '月薪3000-5000元，享受五险一金等基本福利。',
            },
            {
                'job_title': '财务审计岗',
                'category': PublicInstitutionJobCategory.PROFESSIONAL_TECH.value,
                'employment_type': '正式编制',
                'job_location': '某市市区',
                'num_positions': '2',
                'degree_requirement': '本科及以上学历',
                'major_requirement': '会计学、财务管理、审计学等相关专业',
                'age_requirement': '35周岁以下',
                'job_responsibilities': '负责财务核算、预算管理、内部审计等工作。',
                'salary_and_benefits': '月薪5500-9000元，享受五险一金、年终奖金等福利待遇。',
            },
            {
                'job_title': '人事管理岗',
                'category': PublicInstitutionJobCategory.MANAGEMENT.value,
                'employment_type': '正式编制',
                'job_location': '某市市区',
                'num_positions': '1',
                'degree_requirement': '本科及以上学历',
                'major_requirement': '人力资源管理、行政管理、心理学等相关专业',
                'age_requirement': '35周岁以下',
                'job_responsibilities': '负责人员招聘、培训管理、绩效考核、劳动关系等工作。',
                'salary_and_benefits': '月薪5000-8500元，享受五险一金、培训机会等福利待遇。',
            },
        ]
        
        # 生成招聘公告
        job_posts = []
        for i in range(job_posts_count):
            template = job_post_templates[i % len(job_post_templates)]
            
            # 生成随机日期
            start_date = date.today() - timedelta(days=random.randint(1, 30))
            end_date = start_date + timedelta(days=random.randint(7, 30))
            
            job_post = JobPost.objects.create(
                title=f"{template['title']} (第{i+1}批)",
                category=template['category'],
                organization=template['organization'],
                publish_date=start_date,
                application_start_date=start_date,
                application_end_date=end_date,
                source_url=f"https://example.com/job-post/{i+1}",
            )
            job_posts.append(job_post)
            
            # 为每个招聘公告生成岗位
            for j in range(jobs_per_post):
                job_template = job_templates[j % len(job_templates)]
                
                JobInfo.objects.create(
                    job_post=job_post,
                    organization=job_post.organization,
                    job_title=f"{job_template['job_title']} (岗位{j+1})",
                    employment_type=job_template['employment_type'],
                    has_staffing_quota=job_template['employment_type'] == '正式编制',
                    category=job_template['category'],
                    job_location=job_template['job_location'],
                    num_positions=job_template['num_positions'],
                    is_targeted_recruitment=random.choice([True, False]),
                    targeted_recruitment_scope="定向招聘范围：面向特定群体或地区" if random.choice([True, False]) else None,
                    registration_methods="网上报名",
                    registration_materials="身份证、学历证书、学位证书、相关资格证书等",
                    contacts=f"张老师{j+1}",
                    contact_methods=f"联系电话：1380000{1000+i*10+j:04d}",
                    degree_requirement=job_template['degree_requirement'],
                    min_degree_level=random.choice([level.value for level in DegreeLevel]),
                    major_requirement=job_template['major_requirement'],
                    age_requirement=job_template['age_requirement'],
                    max_age_level=random.choice([level.value for level in AgeLevel]),
                    job_experience_requirement=f"具有{random.randint(1, 5)}年以上相关工作经验",
                    min_job_experience_level=random.choice([level.value for level in JobExperienceLevel]),
                    job_responsibilities=job_template['job_responsibilities'],
                    salary_and_benefits=job_template['salary_and_benefits'],
                    political_status_requirement=random.choice(["中共党员", "不限", "共青团员"]),
                    certificate_requirement=random.choice(["相关职业资格证书", "无特殊要求", "计算机等级证书"]),
                    minimum_service_years_requirement=f"最低服务{random.randint(3, 8)}年",
                    gender_requirement=random.choice(["不限", "男性", "女性"]),
                    other_requirement="身体健康，品行端正，具有良好的沟通协调能力。",
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'成功生成 {job_posts_count} 个招聘公告和 {job_posts_count * jobs_per_post} 个岗位！'
            )
        )
        
        # 显示统计信息
        self.stdout.write(f'招聘公告统计:')
        for category in JobPostCategory:
            count = JobPost.objects.filter(category=category.value).count()
            if count > 0:
                self.stdout.write(f'  {category.value}: {count} 个')
        
        self.stdout.write(f'岗位统计:')
        for category in PublicInstitutionJobCategory:
            count = JobInfo.objects.filter(category=category.value).count()
            if count > 0:
                self.stdout.write(f'  {category.value}: {count} 个')
