from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .models import UserProfile, Match, Friend
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.validators import FileExtensionValidator
from django.contrib import messages
from django.core.exceptions import ValidationError
import requests
import os
from .forms import RegisterForm, LoginForm, localMatchForm
from .consumers import Game, StatsConsumer
from tempfile import NamedTemporaryFile
from django.core.files.base import ContentFile
from back.send_email import send_email
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework.response import Response
import jwt, datetime, json
from django.http.request import QueryDict
from django.http import HttpResponse, JsonResponse
# from rest_framework import status

# *********************************** HOME ***********************************
def HomeView(request):
	context = {}
	print('apres context')
	#def get(self, request):
	if request.method == 'GET':
		user = request.user
		print('username:', user.username)
		print('id:', user.id)
		token = request.COOKIES.get('jwt')
		#token = request.COOKIES.get('CSRF_COOKIE')
		if not token:
			print('no token')
			#return Response({'message': 'Unauthorized'}, status=401)
			#messages.error(request, 'Unauthorized')
			return render(request, 'page.html', context)
		try:
			print('try')
			payload = jwt.decode(token, 'SECRET', algorithms=['HS256'])
		except jwt.ExpiredSignatureError:
			messages.error(request, 'Session expired')
			return render(request, 'page.html', context)
			return Response({'message': 'Session expired'}, status=401)
		except jwt.DecodeError:
			messages.error(request, 'Invalid token')
			return render(request, 'page.html', context)
			return Response({'message': 'Invalid token'}, status=401)
		
		user = UserProfile.objects.filter(id=payload['id']).first()
		serializer = UserSerializer(user)

		if (request.user.is_authenticated):
			print('user is authenticated')
			print('username:', user.username)
			print('id:', user.id)
			context['id'] = user.id
			context['user'] = user
			context['username'] = user.username
			context['avatar'] = user.avatar.url
			context['users'] = UserProfile.objects.all().exclude(username=user.username)
			context['matches'] = match_history(user)
			context['friends'] = friends_list(user)
			context['stats'] = match_stats(user)
			# context['invites'] = invites_list(user)
			# context['invitees'] = invitees_list(user)	

		#print('avant return')
		#return Response(serializer.data, status=200, template_name='page.html', content_type=context)
	return render(request, 'page.html', context) 

# *********************************** LOGIN ***********************************

def LoginView(request):
	print('login view')
	#if request.method == 'GET':
	#	print("GET method not allowed")
	#	return render(request, 'page.html')
	#	#return JsonResponse({'status': 'error', 'message': 'GET method not allowed'})
	if request.method == 'POST':
		#print('POST method')
		loginform = LoginForm(request.POST)
		if loginform.is_valid():
			user=authenticate(
				username=loginform.cleaned_data['username'],
				password=loginform.cleaned_data['password']
			)
			response = Response()
		if user is not None:
			#print('user exist')
			request.session['id'] = user.id
			payload = {
			'id': user.id,
			'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
			'iat': datetime.datetime.utcnow(),
			}
			jwt_token = jwt.encode(payload, 'SECRET', algorithm='HS256')
			
			response.set_cookie(key='jwt', value=jwt_token, httponly=True)
			response.data = {
				'name':'token',
				'value': jwt_token,
				'user': UserSerializer(user).data,
			}
			#print('user exist -> 2FA')
			#return JsonResponse({'status': 'success', 'message': 'go to 2FA', 'token': response.data, 'template_name': 'verify.html'})
			return redirect('verify-view')
		else:
			#print('user does not exist')
			messages.error(request, 'Invalid username or password')
	#return JsonResponse({'status': 'error', 'token': response.data})
	return redirect('home')
	return render(request, 'page.html')

	
def RegisterView(request):
	print('register view')
	if request.method == 'POST':
		registerform = RegisterForm(request.POST)
		if registerform.is_valid():
			username=registerform.cleaned_data['username']
			email=registerform.cleaned_data['email']
			if UserProfile.objects.filter(username=username).exists():
				messages.error(request, 'This username is already used!')
				#return render(request, 'page.html')
				return redirect('home')
			if UserProfile.objects.filter(email=email).exists():
				messages.error(request, 'This email is already used!')
				#return render(request, 'page.html')
				return redirect('home')
			mdp=registerform.cleaned_data['password']
		
			serializer = UserSerializer(data=request.POST)
			new_user = UserProfile.objects.create_user(username=username, password=mdp, email=email)
			login(request, new_user)
			if serializer.is_valid():
				serializer.save()
			
			
				#print('serializer is valid')
			messages.success(request, 'Account created successfully!')
			#return JsonResponse({'status': 'success', 'template_name': 'page.html'})
			#return Response(serializer, status=200, template_name='page.html')
	#return render(request, 'page.html')
	return redirect('home')

def update_profile(request):
	if request.method == 'GET':
		return redirect('home')
	username = request.POST.get('username')
	profile_picture = request.FILES.get('profile_picture')
	if (UserProfile.objects.filter(username=username).exists() and username != request.user.username):
		messages.error(request, 'Username already taken')
		return redirect('home')
	user = request.user
	user.username = username
	if (profile_picture is not None):
		validate = FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])
		try:
			validate(profile_picture)
		except ValidationError as e:
			messages.error(request, 'Invalid file type')
			return redirect('home')
		if user.avatar.url != "/media/avatars/default2.png":
			user.avatar.delete()
		profile_picture.name = user.username
		user.avatar = profile_picture
	user.save()
	return redirect('home')

@login_required
def LogoutView(request):
	response = Response()
	response.delete_cookie('jwt')
	response.data = {logout(request)}
	messages.success(request, 'You are logged out!')
	return redirect('home')

def save_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        return ContentFile(response.content)
    else:
        return None

# never_cache est un décorateur qui indique au navigateur de ne pas mettre en cache la reponse
# à cette view, a chaque fois que la view est appelee, la verification aura lieu.
@never_cache
def auth(request):
	code = request.GET.get('code')
	uid = os.environ.get('UID')
	secret = os.environ.get('SECRET')
	token_url = 'http://api.intra.42.fr/oauth/token'
	data = {
		'grant_type': 'authorization_code',
		'client_id': uid,
		'client_secret': secret,
		'code': code,
		'redirect_uri': 'https://localhost:8001/oauth',
	}
	response = requests.post(token_url, data=data)
	if (response.status_code != 200):
		return HttpResponse('<h1>Failed to get access token</h1>')
	access_token = response.json()['access_token']
	response = requests.get('https://api.intra.42.fr/v2/me', headers={'Authorization': 'Bearer ' + access_token})
	if (response.status_code != 200):
		return HttpResponse('<h1>Failed to get user info</h1>')
	intra_login = response.json()['login']
	intra_email = response.json()['email']
	intra_picture = response.json()['image']['link']
	picture = save_image(intra_picture)
	user = UserProfile.objects.filter(username=intra_login).first()
	if user is None:
		user = UserProfile.objects.create_user(username=intra_login, email=intra_email)
		if (picture is not None):
			if user.avatar.url != "/media/avatars/default2.png":
				user.avatar.delete()
			picture.name = user.username
			user.avatar.save('intra_img.jpg', picture, save=True)
	login(request, user)
	messages.success(request, 'You are now logged in!')
	return redirect('home')

# *********************************** MATCHS ***********************************

def match_history(user):
	user = user.username
	matches = Match.objects.filter(player1=user) | Match.objects.filter(player2=user)
	l = []
	for match in matches:
		time = match.timestamp.strftime('%d/%m/%Y %H:%M')
		if match.player1 == user:
			user_score = match.player1_score
			opponent_score = match.player2_score
			opponent_name = match.player2
		else:
			user_score = match.player2_score
			opponent_score = match.player1_score
			opponent_name = match.player1
		match_result = {
        "opponent_name": opponent_name,
        "opponent_score": opponent_score,
        "user_score": user_score,
        "time": time,
		}
		if (user_score > opponent_score):
			match_result["result"] = "Win"
		elif (user_score < opponent_score):
			match_result["result"] = "Loss"
		l.append(match_result)
	return l
		
def match_stats(user):
	# user = User.objects.filter(username=user).first()
	profiles = UserProfile.objects.filter(username=user)
	userProfile = None
	if profiles.exists():
		userProfile = profiles.first()
	else:
		return None
	won = userProfile.matches_won
	lost = userProfile.matches_lost
	total = won + lost
	tourn = userProfile.tourn_won
	if total == 0:
		won_perc = 0
		lost_perc = 0
	else:
		won_perc = round(won / total * 100)
		lost_perc = round(lost / total * 100)
	matches_hist = match_history(user)
	stats = {
		'won': won,
		'lost': lost,
		'wp': won_perc,
		'lp': lost_perc,
		'tourn': tourn,
		'id': userProfile.id,
		'matches': matches_hist,
    }
	return stats

# *********************************** FRIENDS ***********************************

def friends_list(user):
	friends = Friend.objects.filter(sender=user, status='accepted') | Friend.objects.filter(receiver=user, status='accepted')
	profiles = []
	for friend in friends:
		if friend.sender == user:
			profiles.append(UserProfile.objects.get(username=friend.receiver))
		else:
			profiles.append(UserProfile.objects.get(username=friend.sender))
	friends_l = []
	for profile in profiles:
		friends_l.append(profile)

	invites = Friend.objects.filter(receiver=user, status='pending')
	invites_l = []
	for invite in invites:
		invites_l.append(invite.sender.username)
	
	invitees = Friend.objects.filter(sender=user, status='pending')
	invitees_l = []
	for invitee in invitees:
		invitees_l.append(invitee.receiver.username)
	
	friends_all_status = {
        "friends": friends_l,
        "invitees": invitees_l,
        "invites": invites_l,
		}

	return friends_all_status

@login_required
def handle_invite(request):
	if request.method == 'GET':
		return redirect('home')
	sender = request.POST.get('invite')
	receiver = request.user
	status = request.POST.get('status')
	inv = Friend.objects.filter(sender=UserProfile.objects.get(username=sender), receiver=receiver).first()
	if inv:
		inv.status = status
		inv.save()
	return redirect('home')

@login_required
def send_invite(request):
	if request.method == 'GET':
		return redirect('home')
	receiver = request.POST.get('receiver')
	sender = request.user
	friends_l = friends_list(sender)
	request.session.set_expiry(4)
	for friend in friends_l['friends']:
		if friend.username == receiver:
			messages.error(request, 'User is already your friend')
			return redirect('home')
	invite = Friend.objects.filter(sender=sender, receiver=UserProfile.objects.get(username=receiver), status='pending')
	if invite.exists():
		messages.error(request, 'Invite already sent')
		return redirect('home')
	invite = Friend.objects.filter(sender=UserProfile.objects.get(username=receiver), receiver=sender, status='pending')
	if invite.exists():
		messages.error(request, 'You already have an invite from this user')
		return redirect('home')

	Friend.objects.create(sender=sender, receiver=UserProfile.objects.get(username=receiver), status='pending')
	return redirect('home')


import logging

# Obtenez un objet logger
logger = logging.getLogger(__name__)

def my_view(request):
    logger.debug('Ceci est un message de débogage')
    logger.info('Ceci est un message d\'information')
    logger.warning('Ceci est un message d\'avertissement')
    logger.error('Ceci est un message d\'erreur')
    logger.critical('Ceci est un message critique')