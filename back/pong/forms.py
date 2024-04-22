# back/back/pong/forms.py

from django import forms

class RegularLogin(forms.Form):
   username=forms.CharField(required=True)
   email=forms.EmailField(required=True)
   mdp=forms.CharField(required=True, widget=forms.PasswordInput)
