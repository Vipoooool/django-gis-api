from django.contrib import admin

from .models import User, Interest, UserLine

# Register your models here.
# admin.site.register(Token)
admin.site.register([User, Interest, UserLine])
