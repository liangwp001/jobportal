# Generated manually for JobBrowseHistory model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_add_employer_fields'),
        ('jobs', '0003_remove_job_experience_level_alter_category_icon_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobBrowseHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('browsed_date', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='browse_history', to='jobs.job')),
                ('job_seeker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='browse_history', to='accounts.jobseeker')),
            ],
            options={
                'ordering': ['-browsed_date'],
            },
        ),
        migrations.AddIndex(
            model_name='jobbrowsehistory',
            index=models.Index(fields=['job_seeker', '-browsed_date'], name='jobs_jobbrow_job_see_8b8b0a_idx'),
        ),
    ]

