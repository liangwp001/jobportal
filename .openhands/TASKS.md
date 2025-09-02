# Task List

1. ✅ Add production-ready Dockerfile and entrypoint, compose file, and requirements.txt
Added Dockerfile, docker-entrypoint.sh, docker-compose.yml, requirements.txt
2. ✅ Configure Django settings for Docker and env vars (ALLOWED_HOSTS, DEBUG, SECRET_KEY, static handling)
core/settings.py now uses env, whitenoise, dj-database-url, static settings updated
3. ✅ Set site language/timezone to Simplified Chinese and Asia/Shanghai
LANGUAGE_CODE zh-hans, TIME_ZONE Asia/Shanghai, USE_I18N True
4. 🔄 Translate base layout and shared includes to Chinese

5. ⏳ Translate jobs templates (home, list, detail, sections, categories, companies, company detail, post job, find jobs)

6. ⏳ Translate accounts templates (login, signup flows)

7. ⏳ Translate dashboards (employer and job seeker) to Chinese

8. ✅ Create static directory to satisfy STATICFILES_DIRS and smooth collectstatic


