from django.contrib import admin
from .models import User, Match, Friend
from .models import Tournament
# Register your models here.

admin.site.register(User)
admin.site.register(Match)
admin.site.register(Friend)
admin.site.register(Tournament)
