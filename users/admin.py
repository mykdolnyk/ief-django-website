from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, RegistrationApplication
# Register your models here.

admin.site.unregister(User)


class UserProfileInline(admin.TabularInline):
    model = UserProfile
    
    
class RegistrationApplicationInline(admin.TabularInline):
    model = RegistrationApplication


class UserAdmin(UserAdmin):
    list_display = ['username', 'email', 'profile', 'is_staff']
    inlines = (UserProfileInline, RegistrationApplicationInline)
    

class RegistrationApplicationAdmin(admin.ModelAdmin):
    model = RegistrationApplication
    

admin.site.register(User, UserAdmin)
admin.site.register(RegistrationApplication, RegistrationApplicationAdmin)
