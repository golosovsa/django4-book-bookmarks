from django import forms
from django.contrib.auth.models import User

from account.models import Profile


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']

    def clean_password2(self):
        cleaned_data = self.cleaned_data
        if cleaned_data['password'] != cleaned_data['password2']:
            raise forms.ValidationError("Password don't match.")
        return cleaned_data['password2']

    def clean_email(self):
        cleaned_data = self.cleaned_data
        if User.objects.filter(email=cleaned_data['email']).exists():
            raise forms.ValidationError('Email already in use.')
        return cleaned_data['email']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        cleaned_data = self.cleaned_data
        if User.objects.exclude(pk=self.instance.pk).filter(email=cleaned_data['email']).exists():
            raise forms.ValidationError('Email already in use.')
        return cleaned_data['email']


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['date_of_birth', 'photo']
