from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.http import HttpResponse
import os
import requests
from django.contrib import messages
from django.http import HttpResponse
from .models import UserProfile
from .forms import RegisterForm, LoginForm
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


User = get_user_model()

# *********************************** LOGIN ***********************************

# Utilisation des fonctions is_valide(), authenticate() avec "is not None"
# fonctions et outils de Python/Django
def login_user(request):
	loginform = LoginForm(request.POST)
	if request.method == 'POST':
		#loginform = LoginForm(request.POST)
		username = request.POST.get('username')
		password = request.POST.get('password')
		if loginform.is_valid():
			user=authenticate(request, username=username, password=password)
			if user is not None:
				request.session['pk'] = user.pk
				login(request, user)
				messages.success(request, 'Connected!')
				return redirect('home')
			else:
				messages.error(request, 'Invalid username or password')
	return render(request, 'accounts/login.html', {'form': loginform})

def signup(request):
	if request.method == 'POST':
		registerform = RegisterForm(request.POST)
		if registerform.is_valid():
			username=registerform.cleaned_data['username']
			email=registerform.cleaned_data['email']
			mdp=registerform.cleaned_data['password']
			if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
				messages.error(request, 'User already exists')
				return redirect('home')
			new_user = User.objects.create_user(username=username, password=mdp, email=email)
			UserProfile.objects.create(user=new_user)
			login(request, new_user)
			messages.success(request, 'Account created successfully!')
			return redirect('home')
		else:
			messages.error(request, 'Invalid form data')
	else:
		registerform = RegisterForm()
	return render(request, 'accounts/signup.html')


@login_required
def logout_user(request):
	logout(request)
	return redirect('home')

@login_required
def edit_profile(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		profile_picture = request.FILES.get('avatar')
		if (profile_picture is not None):
			validate = FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])
			try:
				validate(profile_picture)
			except ValidationError as e:
				messages.error(request, 'Invalid file type')
				return redirect('home')
		if User.objects.filter(username=username).exists() and username != request.user.username:
			messages.error(request, 'Username already taken')
			return redirect('home')
		user = request.user
		user.username = username
		if profile_picture is not None:
			user_profile = UserProfile.objects.get(user=user)
			if user_profile.avatar != "avatars/default.png":
				user_profile.avatar.delete()
			profile_picture.name = user.username
			user_profile.avatar = profile_picture
			user_profile.save()
		else:
			user.save()
		return redirect('home')
	return render(request, 'accounts/edit_profile.html')
	

# never_cache est un décorateur qui indique au navigateur de ne pas mettre en cache la reponse
# à cette view, a chaque fois que la view est appelee, la verification aura lieu.
@never_cache
def auth(request):
	code = request.GET.get('code')
	uid = os.environ.get('UID')
	secret = os.environ.get('SECRET')
	token_url = 'https://api.intra.42.fr/oauth/token'
	data = {
		'grant_type': 'authorization_code',
		'client_id': uid,
		'client_secret': secret,
		'code': code,
		'redirect_uri': 'http://localhost:8000/oauth',
	}
	response = requests.post(token_url, data=data)
	if (response.status_code != 200):
		return HttpResponse('<h1>Failed to get access token</h1>')
	access_token = response.json()['access_token']
	response = requests.get('https://api.intra.42.fr/v2/me', headers={'Authorization': 'Bearer ' + access_token})
	if (response.status_code != 200):
		return HttpResponse('<h1>Failed to get user info</h1>')
	intra_login = response.json()['login']
	user = User.objects.filter(username=intra_login).first()
	if user is None:
		user = User.objects.create_user(username=intra_login)
		UserProfile.objects.create(user=user)
	login(request, user)
	return redirect('home')