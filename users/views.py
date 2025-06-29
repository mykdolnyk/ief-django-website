from typing import Any
from django.db.models.query import QuerySet
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from .forms import UserRegistrationForm
from .models import User, UserProfile
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.generic.list import ListView
from .helpers import users

# Create your views here.

class UserListView(ListView):
    model = User
    template_name = 'users/user_list.html'
    
    def get_queryset(self) -> QuerySet[Any]:
        # The queryset excludes users that are inactive or do not have a profile
        queryset = super().get_queryset().filter(is_active=True,
                                                 profile__isnull=False)
        
        return queryset
    

def user_page(request: HttpRequest, slug: str):
    try:
        profile = UserProfile.objects.get(slug=slug.lower())
    except UserProfile.DoesNotExist:
        raise Http404()
    
    return HttpResponse(profile.user.username)


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
                user = users.register_user(form)
                
            except Exception as exc:
                # TODO: Log the exception in to some file
                print(exc)
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
        #     if User.objects.get(username=form.cleaned_data['username']).application.status < 4:
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
