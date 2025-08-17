from django import forms
from django.contrib.auth.models import User
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _

# authorization
from .models import Company


class SignupForm(forms.ModelForm):
    company = forms.CharField(required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
        ]

    def clean_company(self):
        company = self.cleaned_data.get('company')
        if Company.objects.filter(name=company).exists():
            raise forms.ValidationError('A company with this name already exists.')
        return company

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # validate if email is correct
        email_validator = EmailValidator()
        try:
            email_validator(username)
        except forms.ValidationError:
            raise forms.ValidationError('Username must be a valid email address.')

        if User.objects.filter(username=username).exists() and self.instance.pk is None:
            raise forms.ValidationError('A user with this username already exists.')
        return username

    def save(self):
        instance = super(SignupForm, self).save(commit=False)
        instance.email = instance.username
        instance.save()
        return instance


class CompanyForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            "placeholder": _("Enter company name")
        })
    )
    
    class Meta:
        model = Company
        fields = "__all__"

    def save(self):
        instance = super(CompanyForm, self).save(commit=False)
        instance.save()
        return instance
