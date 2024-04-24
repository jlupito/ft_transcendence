# back/back/pong/forms.py

from django import forms

class RegisterForm(forms.Form):
   username=forms.CharField(required=True)
   email=forms.EmailField(required=True)
   password=forms.CharField(required=True, widget=forms.PasswordInput)

class LoginForm(forms.Form):
   username=forms.CharField(required=True)
   password=forms.CharField(required=True, widget=forms.PasswordInput)
