# back/back/pong/forms.py

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

class UploadPhotoForm(forms.ModelForm):
	class Meta:
		model = get_user_model()
		fields = ['avatar',]
class RegisterForm(forms.Form):
	class Meta(UserCreationForm.Meta):
		model = get_user_model()
		fields = ['username', 'email', 'password']

#   username=forms.CharField(max_length=25, required=True)
#   email=forms.EmailField(required=True)
#   password=forms.CharField(required=True, widget=forms.PasswordInput)

class LoginForm(forms.Form):
   username=forms.CharField(max_length=25, required=True)
   password=forms.CharField(required=True, widget=forms.PasswordInput)

class localMatchForm(forms.Form):
   local_player2_name=forms.CharField(max_length=25, required=True)
