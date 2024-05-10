from django.shortcuts import redirect
from django.contrib import messages
from .models import Friend
from django.contrib.auth.models import AbstractUser
from users.models import UserProfile
from django.contrib.auth.models import User

def friends_list(user):
	friends = Friend.objects.filter(sender=user, status='accepted') | Friend.objects.filter(receiver=user, status='accepted')
	profiles = []
	for friend in friends:
		if friend.sender == user:
			profiles.append(UserProfile.objects.get(user=friend.receiver))
		else:
			profiles.append(UserProfile.objects.get(user=friend.sender))
	l = []
	for profile in profiles:

		l.append(profile)
	return l

def invites_list(user):
	invites = Friend.objects.filter(receiver=user, status='pending')
	l = []
	for invite in invites:
		l.append(invite.sender.username)
	return l

def invitees_list(user):
    invitees = Friend.objects.filter(sender=user, status='pending')
    l = []
    for invitee in invitees:
        l.append(invitee.receiver.username)
    return l

def handle_invite(request):
	if request.method == 'GET':
		return redirect('home')
	sender = request.POST.get('invite')
	receiver = request.user
	status = request.POST.get('status')
	inv = Friend.objects.filter(sender=User.objects.get(username=sender), receiver=receiver).first()
	inv.status = status
	inv.save()
	return redirect('home')

def send_invite(request):
	if request.method == 'GET':
		return redirect('home')
	receiver = request.POST.get('receiver')
	sender = request.user
	friends_l = friends_list(sender)
	request.session.set_expiry(4)
	for friend in friends_l:
		if friend.user.username == receiver:
			messages.error(request, 'User is already your friend')
			return redirect('home')
	invite = Friend.objects.filter(sender=sender, receiver=User.objects.get(username=receiver), status='pending')
	if invite.exists():
		messages.error(request, 'Invite already sent')
		return redirect('home')
	invite = Friend.objects.filter(sender=User.objects.get(username=receiver), receiver=sender, status='pending')
	if invite.exists():
		messages.error(request, 'You already have an invite from this user')
		return redirect('home')

	Friend.objects.create(sender=sender, receiver=User.objects.get(username=receiver), status='pending')
	return redirect('home')