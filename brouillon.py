from django.contrib.auth.models import User
from .models import UserProfile

def create_user_profile(username, password, email):
    user = User.objects.create_user(username=username, password=password, email=email)
    UserProfile.objects.create(user=user)
    return user

def create_account(request):
    if request.method == 'POST':
        loginform = RegularLogin(request.POST)
        if loginform.is_valid():
            username = loginform.cleaned_data['username']
            password = loginform.cleaned_data['password']
            email = loginform.cleaned_data['email']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                # Appeler la fonction pour créer un nouveau compte
                user = create_user_profile(username, password, email)
                # Connecter automatiquement l'utilisateur nouvellement créé
                login(request, user)
                return redirect('home')
    else:
        form = RegularLogin()
    return render(request, 'home', {'loginform': loginform})

# identification via le mail et pas via le username
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

class EmailAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
