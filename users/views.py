from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from .forms import UserRegistrationForm, UserRegistrationFormOld
from .models import RegistrationApplication, UserProfile, User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .helpers import mcuser

# Create your views here.

def user_list(request: HttpRequest):
    pass


def user_page(request: HttpRequest, id: int):
    pass


def user_award_list(request: HttpRequest, id: int):
    pass


def user_friend_list(request: HttpRequest, id: int):
    pass


def user_media_list(request: HttpRequest, id: int):
    pass


def user_post_list(request: HttpRequest, id: int):
    pass


def user_edit(request: HttpRequest, id: int):
    pass


def user_notifications(request: HttpRequest):
    pass


def register_page(request: HttpRequest):
    """The registration page."""
    if request.user.is_authenticated:
        return redirect(reverse('logout_page'))
    
    context = {}
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        
        if form.is_valid():
            # Save the User, the Application and Profile instances
            try:
                user: User = form.save() # Save the user from the form to the instance
                user.is_active = False # Make the client inactive until the application is reviewed
                user.save() # Save the user from the instance to the DB (required to get the PK)

                RegistrationApplication.objects.create(
                    user = user,
                    text = form.cleaned_data['application'],
                ).save()
                
                UserProfile.objects.create(
                    user=user,
                    mcuuid=mcuser.username_to_mc_uuid(user.username),
                ).save()
                
            except Exception as exc:
                # In case some error occures, the User instance should be deleted as it was
                # already saved, but the registration failed
                user.delete()
                form.add_error(field=None, error='Some unknown error occured. Please try again a bit later.')
            
    elif request.method == 'GET':
        form = UserRegistrationForm()
        
    context['form'] = form

    return render(request, 'users/logreg/register_page.html', context=context)


def login_page(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect(reverse('logout_page'))
    
    context = {}
    
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            login(request, form.get_user())
        # else:
        #     # If User's application status is not 'reviewed', show the corresponind message:
        #     if User.objects.get(username=form.cleaned_data['username']).application.get().status < 4:
        #         form.add_error(field=None, error=form.error_messages['inactive'])
            

    elif request.method == 'GET':
        form = AuthenticationForm()
        
    context['form'] = form
    
        
    return render(request, 'users/logreg/login_page.html', context=context)
    
    
@login_required
def logout_page(request: HttpRequest):
    context = {}
    
    if request.method == 'POST':
        if request.POST.get('yes'):
            logout(request)
            return redirect(reverse('register_page'))
        
        elif request.POST.get('no'):
            return redirect(reverse('user_page'))
    
    return render(request, 'users/logreg/logout_page.html', context=context)
