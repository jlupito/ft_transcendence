from django.shortcuts import render, redirect
from pong.models import UserProfile
from back.send_email import send_email
from .forms import CodeForm
from django.contrib.auth import login
from django.contrib import messages


def verify_view(request):
	form = CodeForm(request.POST or None)
	id = request.session.get('id')
	if id:
		user = UserProfile.objects.get(id=id)
		code_obj = user.code
		code_user = f"{user.username}: {user.code}"
		if not request.POST:
			print(code_user)
			send_email(code_user, user.email)
			print('EMAIL IS SENDING!!!!')
		if form.is_valid():
			print('FORM IS VALID!!!!')
			code = form.cleaned_data.get('code')
			print('ICIIIIII')
			if str(code_obj) == code:
				code_obj.save()
				print('LAAAAAAA!!!!')
				login(request, user)
				print('LOGIN OK!!!!')
				messages.success(request, 'You are now logged in!')
				print('REDIRECT HOME!!!!')
				return redirect('home')		
	print('RENDER VERIFY!!!!')
	return render(request, 'doubleFa/verify.html', {'form': form})