![screencapture-127-0-0-1-8000-jobs-2024-12-05-10_17_20](https://github.com/user-attachments/assets/989e336a-d8e8-4054-91cd-ec100af51b57)
![screencapture-127-0-0-1-8000-jobs-post-2024-12-05-10_17_39](https://github.com/user-attachments/assets/5b075b5b-412b-4888-97fd-50479a3f4e52)
![screencapture-127-0-0-1-8000-dashboard-employer-2024-12-05-10_17_53](https://github.com/user-attachments/assets/69b9a5f4-0485-4708-b488-27d91372453b)
![screencapture-127-0-0-1-8000-accounts-login-2024-12-05-10_18_23](https://github.com/user-attachments/assets/9a40dc07-147d-4d08-8650-396e83a1e528)
![screencapture-127-0-0-1-8000-accounts-signup-2024-12-05-10_18_34](https://github.com/user-attachments/assets/a29a0093-ed80-4e23-ad3a-2567cbfe2646)
![screencapture-127-0-0-1-8000-accounts-signup-jobseeker-2024-12-05-10_18_48](https://github.com/user-attachments/assets/c50dca25-56af-4953-a375-e429a3586f27)
![screencapture-127-0-0-1-8000-accounts-signup-employer-2024-12-05-10_19_12](https://github.com/user-attachments/assets/eab4b12f-6306-44bb-936e-bbe4856ea6ce)
![screencapture-127-0-0-1-8000-dashboard-jobseeker-2024-12-05-10_19_56](https://github.com/user-attachments/assets/c8a9c821-c015-45df-ae4f-3d27299c3ef1)
![screencapture-127-0-0-1-8000-jobs-1-2024-12-05-10_21_09](https://github.com/user-attachments/assets/8118b19a-8352-4a86-b073-1de29f2b1359)
![screencapture-127-0-0-1-8000-2024-12-05-16_51_49](https://github.com/user-attachments/assets/ee6ea4c3-c0c9-43be-9bd3-36cc8db4da27)
![screencapture-127-0-0-1-8000-companies-2024-12-05-17_15_05](https://github.com/user-attachments/assets/5b8c71ed-ba44-48e4-9ba9-7bcd06ae1777)
![screencapture-127-0-0-1-8000-companies-1-2024-12-05-17_15_23](https://github.com/user-attachments/assets/bde2d5dc-6a2a-4087-933a-c4031d02c22a)
![screencapture-127-0-0-1-8000-jobs-2024-12-05-18_13_28](https://github.com/user-attachments/assets/bb3eba73-dd89-444b-9b7b-cddfe98b1411)
![screencapture-127-0-0-1-8000-2024-12-05-16_51_49](https://github.com/user-attachments/assets/d0fdf746-31ff-4c9f-92ce-d161c58fb5fc)
 Job Portal

A modern job portal built with Django and Tailwind CSS, designed to connect job seekers with employers efficiently.

 Features

- User Authentication: Separate sign-up and login for job seekers and employers.
- Job Posting and Management: Employers can post and manage job listings.
- Job Search and Filtering: Users can search for jobs using keywords and location filters.
- Application Tracking: Job seekers can apply for jobs and track their applications.
- Responsive Design: Optimized for both desktop and mobile devices.
- User Profiles: Detailed profiles for both job seekers and employers.

 Tech Stack

- Backend: Django
- Frontend: Tailwind CSS, DaisyUI, Alpine.js
- Database: SQLite (default, can be configured for other databases)
- Icons: Font Awesome

## 开发规则

本项目遵循严格的开发规则和标准，确保代码质量和项目一致性。详细规则请参考：

- [项目规则总览](PROJECT_RULES.md) - 完整的项目开发规则
- [规则目录](rules/) - 分类的规则文件
- [.cursorrules](.cursorrules) - Cursor AI 规则配置

### 核心规则摘要
1. **架构**: 使用Django应用模块化架构，apps/目录组织
2. **模板**: 扩展base.html，使用TailwindCSS+DaisyUI，禁止自定义CSS
3. **安全**: 启用CSRF，邮箱验证，频率限制
4. **国际化**: 中文界面，zh-hans语言，Asia/Shanghai时区
5. **开发**: 遵循PEP 8，Django最佳实践，完整测试覆盖

 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/jobportal.git
   cd jobportal
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

6. Access the application:
   Open your web browser and go to `http://127.0.0.1:8000/`.

Usage

- Job Seekers: Register, search for jobs, and apply directly through the platform.
- Employers: Register, post job listings, and manage applications from job seekers.

 Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Acknowledgments

- Thanks to the Django and Tailwind CSS communities for their excellent tools and documentation.
- Icons provided by Font Awesome.



