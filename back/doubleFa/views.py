from django.shortcuts import render, redirect
from pong.models import UserProfile
from back.send_email import send_email
from .forms import CodeForm
from django.contrib.auth import login
from django.contrib import messages
import jwt, datetime, json
from django.http.request import QueryDict
from django.http import HttpResponse, JsonResponse
from pong.serializers import UserSerializer
from rest_framework.response import Response

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
		if form.is_valid():
			code = form.cleaned_data.get('number')
			if str(code_obj) == code:
				code_obj.save()
			#	payload = {
			#'id': user.id,
			#'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
			#'iat': datetime.datetime.utcnow(),
			#}
			#jwt_token = jwt.encode(payload, 'SECRET', algorithm='HS256')
			#response = Response()
			#response.set_cookie(key='jwt', value=jwt_token, httponly=True)
			#response.data = {
			#	'name':'token',
			#	'value': jwt_token,
			#	'user': UserSerializer(user).data,
			#}
			login(request, user)
			return redirect('home')
			#return JsonResponse({'status': 'success', 'token': response.data, 'template_name': 'page.html'})
	return render(request, 'verify.html', {'form': form})

