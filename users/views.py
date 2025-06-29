from typing import Any
from django.db.models.query import QuerySet
from django.forms import ValidationError
from django.http import Http404, HttpResponseNotAllowed, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from .forms import ProfileCommentCreationForm, ProfileUpdateForm, UserRegistrationForm, UserUpdateForm
from .models import ProfileComment, User, UserProfile
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from .helpers import users, mcuser
from django.core.files.base import ContentFile
from django.conf import settings


class UserListView(LoginRequiredMixin, ListView):
    model = UserProfile
    template_name = 'users/user_list.html'
    login_url = settings.LOGIN_PAGE_NAME

    def get_queryset(self) -> QuerySet[Any]:
        # The queryset excludes users that are inactive or do not have a profile
        queryset = super().get_queryset().filter(user__is_active=True)

        return queryset


@login_required(login_url=settings.LOGIN_PAGE_NAME)
def user_page(request: HttpRequest, slug: str):
    profile = users.get_userprofile_or_404(slug)

    context = {'profile': profile}

    # TODO: periodical PFP update (caching)

        
    # Load existing comments
    context['comments'] = ProfileComment.objects.filter(profile=profile, is_visible=True).order_by('-created_at').all()
    # Load comment creation form
    context['comment_form'] = ProfileCommentCreationForm()
    
    context['request_user_is_subscribed'] = profile in request.user.profile.subscriptions.all() # The current user is a subscriber of this user
    context['subscribers'] = UserProfile.objects.subscribers(profile)[:3]

    return render(request, 'users/profile/user_page.html', context)


@login_required(login_url=settings.LOGIN_PAGE_NAME)
def create_comment(request: HttpRequest, slug: str):
    if request.method != 'POST':   
        return HttpResponseNotAllowed()

    profile = users.get_userprofile_or_404(slug)

    form = ProfileCommentCreationForm(request.POST)
    
    if form.is_valid():
        new_comment: ProfileComment = form.save(commit=False)
        
        
        new_comment.profile = profile # The comment is created on the profile that is was written on
        new_comment.is_visible = True # It is set to be visible
        new_comment.owner = request.user # The owner of the comment is the request user

        new_comment.save()
        
    return redirect(reverse('user_page', args=(slug,)))


def user_award_list(request: HttpRequest, slug: str):
    profile = users.get_userprofile_or_404(slug)

    pass

@login_required(login_url=settings.LOGIN_PAGE_NAME)
def user_subscribe(request: HttpRequest, slug: str):
    """A view that is responsible for creating and deleting
    subscription instances on POST.
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(('GET',))
    
    profile = users.get_userprofile_or_404(slug)
    
    # A "subscribe" button was pressed:
    if request.POST['action'] == 'post':
        
        if profile.user != request.user:
            request.user.profile.subscriptions.add(profile)
            return redirect(reverse('user_page', args=(slug,)))
        
        else:
            return HttpResponseNotAllowed(('GET',))

    # An "unsubscribe" button was pressed:
    elif request.POST['action'] == 'delete':
        
        if profile.user != request.user:
            request.user.profile.subscriptions.remove(profile)
    
            return redirect(reverse('user_page', args=(slug,)))


@login_required(login_url=settings.LOGIN_PAGE_NAME)
def user_followings(request: HttpRequest, slug: str):
    """A view that is responsible for showing a subscription and subscriber lists on GET."""
    profile = users.get_userprofile_or_404(slug)

    subscription_list = profile.subscriptions.filter()
    subscriber_list = UserProfile.objects.subscribers(profile)
        
    context = {'profile': profile,
                'subscriber_list': subscriber_list,
                'subscription_list': subscription_list}

    return render(request, 'users/profile/user_followings.html', context=context)


def user_media_list(request: HttpRequest, slug: str):
    profile = users.get_userprofile_or_404(slug)

    pass


def user_post_list(request: HttpRequest, slug: str):
    profile = users.get_userprofile_or_404(slug)

    pass

@login_required(login_url=settings.LOGIN_PAGE_NAME)
def user_edit(request: HttpRequest, slug: str):
    # if UserProfile.objects.get(slug=slug).user.id != request.user.id:
    if request.user.profile.slug != slug:
        return redirect(reverse("user_edit", args=(request.user.profile.slug,)))
    
    if request.method == "POST":

        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        user_form = UserUpdateForm(request.POST, instance=request.user)
        
        if profile_form.is_valid():
            profile_form.save()

        if user_form.is_valid():
            user_form.save()
        
    else:
        # Prepopulate the fields
        profile_form = ProfileUpdateForm(initial={
            "bio": request.user.profile.bio,
            "signing": request.user.profile.signing,
            })
        user_form = UserUpdateForm(initial={
            'username': request.user.username,
            'email': request.user.email,
            })
        
    context = {'profile_form': profile_form, 'user_form': user_form}
        
    return render(request, 'users/profile/user_edit_page.html', context)


@login_required(login_url=settings.LOGIN_PAGE_NAME)
def refresh_pfp(request: HttpRequest, slug: str):
    profile = users.get_userprofile_or_404(slug)
    
    if profile == request.user.profile:
        # Assure that the user is updating his own PFP
        # Is not necessary, as it is possible to just update the PFP of request.user.profile,
        # but for the sake of possible future modifications and clarity it is made this way.
        users.update_pfp(profile=profile)
    return redirect(reverse('user_edit', args=[slug]))


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
                
                if settings.DEBUG: # If Django Debug Mode is ON
                    users.approve_user(user) # ! IS HERE FOR DEBUG PURPOSES, SHOULD BE REMOVED
                    # Automatically approves the user

            except Exception as exc:
                # TODO: Log the exception in to some file
                print(exc)
                form.add_error(
                    field=None, error='Some unknown error occured. Please try again a bit later.')

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


@login_required(login_url=settings.LOGIN_PAGE_NAME)
def logout_page(request: HttpRequest):
    context = {}

    if request.method == 'POST':
        if request.POST.get('yes'):
            logout(request)
            return redirect(reverse('register_page'))

        elif request.POST.get('no'):
            return redirect(reverse('user_page'))

    return render(request, 'users/logreg/logout_page.html', context=context)
