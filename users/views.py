from typing import Any
from django.db.models.query import QuerySet
from django.http import Http404, HttpResponseNotAllowed, HttpRequest, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_not_required
from django.views.generic.list import ListView
from django.views.generic import DetailView
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from blogs.models import Blog
from users.helpers import awards
from users.helpers.notifications import notify_about_comment
from .forms import ProfileCommentCreationForm, ProfileUpdateForm, UploadMediaForm, UserAuthenticationForm, UserRegistrationForm, UserUpdateForm, UserPasswordChangeForm
from .models import Notification, ProfileComment, ProfileMedia, User, UserAward, UserProfile
from .helpers import users
from helpers import form_processing, email


class UserListView(ListView):
    model = UserProfile
    template_name = 'users/user_list.html'
    login_url = settings.LOGIN_PAGE_NAME


def user_page(request: HttpRequest, slug: str):
    profile: UserProfile = users.get_userprofile_or_404(slug)

    post_list = Blog.objects.filter(
        author=profile.user).order_by('-created_at')

    subscribers = profile.subscribers.filter()

    context = {
        'profile': profile,
        # TODO: periodical PFP update (caching)
        'media_list': ProfileMedia.objects.filter(profile=profile, is_visible=True)[:3],
        'comments': ProfileComment.objects.filter(profile=profile),
        'comment_form': ProfileCommentCreationForm(),
        # The current user is a subscriber of this user
        'request_user_is_subscribed': profile in request.user.profile.subscriptions.all(),
        'subscribers': subscribers[:3],
        'post_list': post_list[:3],
    }

    return render(request, 'users/profile/user_page.html', context)


def create_comment(request: HttpRequest, slug: str):
    if request.method != 'POST':
        return HttpResponseNotAllowed()

    profile = users.get_userprofile_or_404(slug)

    form = ProfileCommentCreationForm(request.POST)

    if form.is_valid():
        new_comment: ProfileComment = form.save(commit=False)

        # The comment is created on the profile that is was written on
        new_comment.profile = profile
        new_comment.is_visible = True  # It is set to be visible
        new_comment.owner = request.user  # The owner of the comment is the request user

        new_comment.save()

        notify_about_comment(new_comment)

        awards.grant_user_comment_creation_awards(user=request.user)

    return redirect(reverse('user_page', args=(slug,)))


class UserAwardList(ListView):
    model = UserAward

    context_object_name = 'awards'
    template_name = 'users/profile/user_awards.html'
    login_url = settings.LOGIN_PAGE_NAME

    def get_queryset(self) -> QuerySet[Any]:
        # Get only the awards of the user that is being checked
        user = users.get_userprofile_or_404(self.kwargs["slug"]).user
        return UserAward.objects.filter(user=user)

    def get_context_data(self, **kwargs):
        new_context = super().get_context_data(**kwargs)
        new_context['profile'] = users.get_userprofile_or_404(
            self.kwargs["slug"])
        return new_context


def user_subscribe(request: HttpRequest, slug: str):
    """A view that is responsible for creating and deleting
    subscription instances on POST."""
    profile = users.get_userprofile_or_404(slug)

    response = {
        'success': True,
    }

    if profile not in request.user.profile.subscriptions.all():
        profile.subscribers.add(request.user.profile)
        response['action'] = 'add'
        awards.grant_user_followers_awards(user=profile.user)
    else:
        profile.subscribers.remove(request.user.profile)
        response['action'] = 'remove'

    return JsonResponse(response)


def user_followings(request: HttpRequest, slug: str):
    """A view that is responsible for showing a subscription and subscriber lists on GET."""
    profile = users.get_userprofile_or_404(slug)

    subscription_list = profile.subscriptions.filter()
    subscriber_list = profile.subscribers.filter()

    context = {'profile': profile,
               'subscriber_list': subscriber_list,
               'subscription_list': subscription_list}

    return render(request, 'users/profile/user_followings.html', context=context)


class UserMediaList(ListView):
    model = ProfileMedia
    template_name = 'users/profile/user_profile_media_list.html'
    login_url = settings.LOGIN_PAGE_NAME
    context_object_name = 'media_list'

    def get_queryset(self) -> QuerySet[Any]:
        # Get only the visible media of the user that is being checked
        profile = users.get_userprofile_or_404(
            self.kwargs["slug"]).user.profile
        return ProfileMedia.objects.filter(profile=profile, is_visible=True)

    def get_context_data(self, **kwargs):
        new_context = super().get_context_data(**kwargs)
        new_context['profile'] = users.get_userprofile_or_404(
            self.kwargs["slug"])
        return new_context


class UserMediaDetail(DetailView):
    model = ProfileMedia
    template_name = 'users/profile/user_profile_media_detail.html'
    login_url = settings.LOGIN_PAGE_NAME
    context_object_name = 'media'


def user_media_upload(request: HttpRequest, slug: str):
    profile = users.get_userprofile_or_404(slug)

    if request.user.profile != profile:
        return redirect(reverse("user_media_upload", args=(request.user.profile.slug,)))

    form = UploadMediaForm

    if request.method == 'POST':
        form = UploadMediaForm(request.POST, request.FILES)
        if form.is_valid():
            new_media = form.save(commit=False)
            new_media.profile = profile
            new_media.save()

            awards.grant_user_media_creation_awards(request.user)

            return redirect(reverse('user_media_list', args=(slug,)))
    else:
        form = UploadMediaForm

    context = {
        'page_title': 'Upload Your Picture',
        'form': form,
        'form_action_url': reverse('user_media_upload', args=(slug,)),
    }
    return render(request, 'parts/general_form_page.html', context=context)


def user_media_delete(request: HttpRequest, slug):
    profile: UserProfile = users.get_userprofile_or_404(slug)

    media_list = profile.media_list.filter(is_visible=True)

    context = {"media_list": media_list}

    if request.method == "POST":
        media_to_delete = form_processing.parse_bulk_delete_form(
            request, 'media_')

        for media_id in media_to_delete:
            try:
                media: ProfileMedia = media_list.get(pk=media_id)
                media.delete()
            except ProfileMedia.DoesNotExist:
                # Request to remove media of another user or non-existent one just gets ignored
                pass

        # return redirect(reverse('user_media_list', args=(slug,)))

    return render(request, 'users/profile/user_profile_media_delete.html', context=context)


def user_notification_list(request: HttpRequest):
    # Don't include deleted notifications
    notifications = request.user.notifications.filter(
        is_deleted=False).order_by('-created_at')
    if request.method == "POST":

        if request.POST['action'] == "update":
            # If 'Seen' was clicked
            notifications.filter(is_seen=False).update(is_seen=True)

        elif request.POST['action'] == "delete":
            # If 'Delete' was clicked
            notifs_to_delete = form_processing.parse_bulk_delete_form(
                request, 'notification_')

            for notif_id in notifs_to_delete:
                try:
                    notif: Notification = notifications.get(pk=notif_id)
                    notif.is_deleted = True
                    notif.save()

                except Notification.DoesNotExist:
                    # Request to remove a non-existent notification just gets ignored
                    pass

    context = {
        "not_seen_notifications": notifications.filter(is_seen=False),
        "seen_notifications": notifications.filter(is_seen=True),
    }

    return render(request, "users/notifications/user_notification_list.html", context)


class UserBlogList(ListView):
    model = Blog
    template_name = 'users/profile/user_blogs.html'
    login_url = settings.LOGIN_PAGE_NAME
    context_object_name = 'blogs'

    def get_queryset(self) -> QuerySet[Any]:
        self.user = get_object_or_404(User, profile__slug=self.kwargs['slug'])
        return super().get_queryset().filter(author=self.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.user
        return context


def user_edit(request: HttpRequest, slug: str):
    # if UserProfile.objects.get(slug=slug).user.id != request.user.id:
    if request.user.profile.slug != slug:
        return redirect(reverse("user_edit", args=(request.user.profile.slug,)))

    if request.method == "POST":

        if request.POST['updating'] == 'user':
            # Updating the User/UserProfile info
            profile_form = ProfileUpdateForm(
                request.POST, instance=request.user.profile)
            user_form = UserUpdateForm(request.POST, instance=request.user)
            password_change_form = UserPasswordChangeForm()

            if profile_form.is_valid() and user_form.is_valid():
                profile_form.save()
                user_form.save()
                messages.success(
                    request, 'Your profile has been successfully updated.')
                return redirect(reverse('user_page', args=(slug,)))

        elif request.POST['updating'] == 'password':
            # Updating the password
            password_change_form = UserPasswordChangeForm(
                request.POST, instance=request.user)

            # Prepopulate the fields
            profile_form = ProfileUpdateForm(initial={
                "bio": request.user.profile.bio,
                "signing": request.user.profile.signing,
            })
            user_form = UserUpdateForm(initial={
                'username': request.user.username,
                'email': request.user.email,
            })

            if password_change_form.is_valid():
                password_change_form.save()
                messages.success(
                    request, 'Your password has been successfully updated.')
                return redirect(reverse('user_page', args=(slug,)))

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
        password_change_form = UserPasswordChangeForm()

    context = {'profile_form': profile_form, 'user_form': user_form,
               'password_change_form': password_change_form}

    return render(request, 'users/profile/user_edit_page.html', context)


def refresh_pfp(request: HttpRequest, slug: str):
    profile = users.get_userprofile_or_404(slug)

    if profile == request.user.profile:
        # Assure that the user is updating his own PFP
        # Is not necessary, as it is possible to just update the PFP of request.user.profile,
        # but for the sake of possible future modifications and clarity it is made this way.
        try:
            users.update_pfp(profile=profile)
            messages.success(
                request, 'Your profile picture has been refreshed.')
        except Exception as exc:  # TODO: log that somewhere
            print(exc)
            messages.error(
                request, 'An error occured when trying to refresh your profile picture. Please try again later.')
    return redirect(reverse('user_edit', args=[slug]))


class TimelinePage(ListView):
    template_name = 'users/timeline.html'
    context_object_name = 'blogs'
    login_url = settings.LOGIN_PAGE_NAME

    def get_queryset(self):
        return Blog.objects.filter(
            author__profile__in=self.request.user.profile.subscriptions.all()).order_by('-created_at')[:50]


@login_not_required
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
                email.send_registration_confirmation_email(user=user)

                if settings.DEBUG:  # If Django Debug Mode is ON
                    # ! IS HERE FOR DEBUG PURPOSES, SHOULD BE REMOVED IN PRODUCTION
                    # user.application.status = 1 # In this case, the signal doesn't approve the user automatically
                    user.application.save()  # But calling the `save` method does
            except Exception as exc:
                # TODO: Log the exception in to some file
                print(exc)
                form.add_error(
                    field=None, error='Some unknown error occured. Please try again a bit later.')

            return render(request, 'users/logreg/register_page_confirm.html', context=context)

    elif request.method == 'GET':
        form = UserRegistrationForm()

    context['form'] = form

    return render(request, 'users/logreg/register_page.html', context=context)


@login_not_required
def login_page(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect(reverse('logout_page'))

    context = {}

    if request.method == 'POST':
        form = UserAuthenticationForm(data=request.POST)

        if form.is_valid():
            user: User = form.get_user()

            try:
                # Prevent users without a profile from logging in using
                # the default login page (like superusers created via console line)
                user.profile
            except ObjectDoesNotExist:
                form.add_error('', form.get_invalid_login_error())
            else:
                login(request, user)
                next = request.GET.get('next')
                return redirect(next or reverse('index_page'))

    elif request.method == 'GET':
        form = UserAuthenticationForm()

    context['form'] = form

    return render(request, 'users/logreg/login_page.html', context=context)


def logout_page(request: HttpRequest):
    context = {}

    if request.method == 'POST':
        if request.POST.get('yes'):
            logout(request)
            return redirect(reverse('login_page'))

        elif request.POST.get('no'):
            return redirect(reverse('user_page', args=(request.user.profile.slug,)))

    return render(request, 'users/logreg/logout_page.html', context=context)


class PasswordReset(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/logreg/reset_password_page.html'
    subject_template_name = 'email/reset_password_subject.html'

    html_email_template_name = 'email/reset_password_email.html'
    email_template_name = 'email/reset_password_email.html'

    success_url = '/'
    success_message = "The password reset email will be sent out to your mailbox shortly."


class PasswordResetConfirm(SuccessMessageMixin, PasswordResetConfirmView):
    template_name = 'users/logreg/reset_password_confirmation.html'
    success_url = '/'
    success_message = "The password has been successfully reset! Feel free to Log In now."

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('logout_page'))

        return super().dispatch(request, *args, **kwargs)
