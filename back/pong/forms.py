# back/back/pong/forms.py

from django import forms

class LocalMatchForm(forms.Form):
   local_player2_name=forms.CharField(max_length=25, required=True)
