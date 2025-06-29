from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import AwardType, UserAward, UserProfile, RegistrationApplication
from .forms import UserRegistrationForm


class UserProfileInline(admin.TabularInline):
    model = UserProfile


# class FriendInline(admin.TabularInline):
#     model = Friend
#     fk_name = 'user'


class RegistrationApplicationInline(admin.TabularInline):
    model = RegistrationApplication


class UserAdmin(UserAdmin):
    list_display = ['username', 'email', 'profile', 'is_staff']
    # inlines = (UserProfileInline, FriendInline, RegistrationApplicationInline)
    inlines = (UserProfileInline, RegistrationApplicationInline)
    

    add_form = UserRegistrationForm


class RegistrationApplicationAdmin(admin.ModelAdmin):
    model = RegistrationApplication
    
    
class AwardTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    
    model = AwardType


class UserAwardAdmin(admin.ModelAdmin):
    model = UserAward


admin.site.unregister(User)

admin.site.register(User, UserAdmin)
admin.site.register(RegistrationApplication, RegistrationApplicationAdmin)

admin.site.register(AwardType, AwardTypeAdmin)
admin.site.register(UserAward, UserAwardAdmin)
