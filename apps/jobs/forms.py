from django import forms
from .models import JobInfo, JobPost, Application, PublicInstitutionJobCategory

class JobForm(forms.ModelForm):
    class Meta:
        model = JobInfo
        fields = [
            'job_title', 'category', 'job_responsibilities', 'other_requirement',
            'job_location', 'salary_and_benefits', 'employment_type'
        ]
        widgets = {
            'job_responsibilities': forms.Textarea(attrs={'rows': 4}),
            'other_requirement': forms.Textarea(attrs={'rows': 4}),
        }

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(
                attrs={'rows': 4, 'placeholder': 'Write your cover letter here...'}
            )
        }

class JobSearchForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Job title or keyword'}
    ))
    location = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Location'}
    ))
    category = forms.ChoiceField(
        required=False,
        choices=[('', 'All Categories')] + [(tag.value, tag.value) for tag in PublicInstitutionJobCategory]
    )
    job_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + [('事业编', '事业编'), ('劳务派遣', '劳务派遣'), ('人事代理', '人事代理'), ('合同制', '合同制')]
    )

class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobPost
        fields = ['title', 'organization', 'publish_date', 'application_start_date', 'application_end_date', 'category']
        widgets = {
            'publish_date': forms.DateInput(attrs={'type': 'date'}),
            'application_start_date': forms.DateInput(attrs={'type': 'date'}),
            'application_end_date': forms.DateInput(attrs={'type': 'date'}),
        }