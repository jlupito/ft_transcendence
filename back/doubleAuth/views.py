from django.shortcuts import render, redirect
from back import send_email
from doubleAuth.forms import DoubleAuthForm
from users.models import UserProfile
from django.contrib import messages
from django.contrib.auth import login

def verify_view(request):
	form = DoubleAuthForm(request.POST or None)
	pk = request.session.get('pk')
	if pk:
		user = UserProfile.objects.get(pk=pk)
		code = user.code
		code_user = f"{user.username}: {user.code}"
		if not request.POST:
			print(code_user)
			send_email(code_user, user.email)
		if form.is_valid():
			num = form.cleaned_data.get('number')

			if str(code) == num:
				code.save()
				login(request, user)
				return redirect('home')
			else:
				messages.error(request, 'Invalid code')
				return redirect('login')
	return render(request, 'accounts/verify.html', {'form': form})
