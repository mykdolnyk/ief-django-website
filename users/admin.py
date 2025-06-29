from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from django.db import models
from .models import AwardType, ProfileMedia, UserAward, UserProfile, RegistrationApplication
from .forms import UserRegistrationForm


class UserProfileInline(admin.TabularInline):
    model = UserProfile
    def get_queryset(self, request):
        # Use all_objects manager that allows to see `is_visible=False` profiles
        queryset = self.model.all_objects.get_queryset()
        
        # From the super method that I don't call here:
        ordering = self.ordering or ()
        if ordering:
            queryset = queryset.order_by(*ordering)
            
        return queryset

class RegistrationApplicationInline(admin.TabularInline):
    model = RegistrationApplication


class UserAdmin(UserAdmin):
    list_display = ['username', 'email', 'profile', 'is_staff']
    inlines = (UserProfileInline, RegistrationApplicationInline)
    
    add_form = UserRegistrationForm


@admin.action(description='Approve selected Applications')
def approve_applications(modeladmin, request, queryset):
    queryset.update(status=1)


@admin.action(description='Reject selected Applications')
def reject_applications(modeladmin, request, queryset):
    queryset.update(status=2)
    

class RegistrationApplicationAdmin(admin.ModelAdmin):
    model = RegistrationApplication
    actions = [approve_applications, reject_applications]
    
    list_filter = ['status']
    list_display = ['user', 'status']
    
    
class AwardTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    
    model = AwardType


class UserAwardAdmin(admin.ModelAdmin):
    model = UserAward


class ProfileMediaAdmin(admin.ModelAdmin):
    list_display = ['profile', 'title', 'is_visible']
    model: ProfileMedia

admin.site.unregister(User)

admin.site.register(User, UserAdmin)
admin.site.register(RegistrationApplication, RegistrationApplicationAdmin)

admin.site.register(AwardType, AwardTypeAdmin)
admin.site.register(UserAward, UserAwardAdmin)

admin.site.register(ProfileMedia, ProfileMediaAdmin)
