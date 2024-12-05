from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Employer, JobSeeker

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

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

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