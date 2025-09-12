# 邮箱验证配置说明

## 功能概述

用户注册时需要通过邮箱验证码验证才能完成注册。系统会向用户邮箱发送6位数字验证码，用户输入正确验证码后才能成功注册。

## 配置步骤

### 1. 邮箱服务器配置

在 `core/settings.py` 中配置邮箱服务器信息：

```python
# 邮箱配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'  # QQ邮箱SMTP服务器
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'your-email@qq.com')  # 发送邮件的邮箱
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'your-app-password')  # 邮箱授权码
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

### 2. 环境变量配置

创建 `.env` 文件或设置环境变量：

```bash
# 邮箱配置
EMAIL_HOST_USER=your-email@qq.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 3. 获取QQ邮箱授权码

1. 登录QQ邮箱
2. 进入"设置" -> "账户"
3. 找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
4. 开启"IMAP/SMTP服务"
5. 按照提示获取授权码
6. 将授权码设置为 `EMAIL_HOST_PASSWORD`

### 4. 其他邮箱服务商配置

#### Gmail
```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

#### 163邮箱
```python
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
EMAIL_USE_TLS = False
```

#### 企业邮箱
```python
EMAIL_HOST = 'smtp.exmail.qq.com'  # 腾讯企业邮箱
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

## 功能特性

### 验证码规则
- 6位数字验证码
- 10分钟有效期
- 最多5次验证尝试
- 1分钟发送间隔限制

### 安全措施
- 验证码只能使用一次
- 达到最大尝试次数后需要重新获取
- 验证码过期后自动失效
- 防止重复发送验证码

### 用户体验
- 实时验证反馈
- 倒计时显示
- 友好的错误提示
- 响应式界面设计

## 测试

运行以下命令测试邮箱验证功能：

```bash
python manage.py shell
```

```python
from apps.accounts.utils import create_or_update_verification
from apps.accounts.models import EmailVerification

# 测试发送验证码
verification = create_or_update_verification('test@example.com')
print(f"验证码: {verification.verification_code}")
```

## 故障排除

### 常见问题

1. **连接被拒绝**
   - 检查邮箱服务器地址和端口
   - 确认网络连接正常

2. **认证失败**
   - 检查邮箱地址和授权码是否正确
   - 确认已开启SMTP服务

3. **邮件发送失败**
   - 检查邮箱是否被限制发送
   - 确认收件人邮箱地址有效

### 调试模式

在开发环境中，可以使用控制台后端：

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

这样邮件会直接打印到控制台，方便调试。

## 生产环境建议

1. 使用专业的邮件服务商（如SendGrid、阿里云邮件推送等）
2. 配置邮件队列处理大量发送
3. 设置邮件发送频率限制
4. 监控邮件发送状态和失败率
5. 配置邮件模板和品牌化设计
