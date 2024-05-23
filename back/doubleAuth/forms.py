from django import forms
from .models import DoubleAuth

class DoubleAuthForm(forms.ModelForm):
	num = forms.CharField(label='Code', help_text='Enter email verification code')
	class Meta:
		model = DoubleAuth
		fields = ('num',)
		