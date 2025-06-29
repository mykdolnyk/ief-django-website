from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpResponseNotAllowed, HttpRequest, JsonResponse
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
from users.helpers import notifications
from .models import Notification, ProfileComment, ProfileMedia, User, UserAward, UserProfile
from .helpers import authentication
from .helpers import profiles
from common import form_processing
from users import tasks
import users.forms as forms
import logging

logger = logging.getLogger(__name__)
login_restriction_logger = logging.getLogger(__name__ + '.login_page')


class UserListView(ListView):
    model = UserProfile
    template_name = 'users/user_list.html'

def user_page(request: HttpRequest, slug: str):
    profile: UserProfile = profiles.get_userprofile_or_404(slug)

    post_list = Blog.objects.filter(
        author=profile.user).order_by('-created_at')

    subscribers = profile.subscribers.filter()

    context = {
        'profile': profile,
        'media_list': ProfileMedia.objects.filter(profile=profile, is_visible=True)[:3],
        'comments': ProfileComment.objects.filter(profile=profile),
        'comment_form': forms.ProfileCommentCreationForm(),
        # The current user is a subscriber of this user
        'request_user_is_subscribed': profile in request.user.profile.subscriptions.all(),
        'subscribers': subscribers[:3],
        'post_list': post_list[:3],
    }

    return render(request, 'users/profile/user_page.html', context)


def create_comment(request: HttpRequest, slug: str):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['post'])

    profile = profiles.get_userprofile_or_404(slug)

    form = forms.ProfileCommentCreationForm(request.POST)

    if form.is_valid():
        new_comment: ProfileComment = form.save(commit=False)

        # The comment is created on the profile that is was written on
        new_comment.profile = profile
        new_comment.is_visible = True  # It is set to be visible
        new_comment.owner = request.user  # The owner of the comment is the request user

        new_comment.save()

        notifications.send_comment_notification(new_comment)

        awards.grant_user_comment_creation_awards(user=request.user)

    return redirect(reverse('user_page', args=(slug,)))


class UserAwardList(ListView):
    model = UserAward

    context_object_name = 'awards'
    template_name = 'users/profile/user_awards.html'

    def get_queryset(self) -> QuerySet[Any]:
        # Get only the awards of the user that is being checked
        user = profiles.get_userprofile_or_404(self.kwargs["slug"]).user
        return UserAward.objects.filter(user=user)

    def get_context_data(self, **kwargs):
        new_context = super().get_context_data(**kwargs)
        new_context['profile'] = profiles.get_userprofile_or_404(
            self.kwargs["slug"])
        return new_context


def user_subscribe(request: HttpRequest, slug: str):
    """A view that is responsible for creating and deleting
    subscription instances on POST."""
    profile = profiles.get_userprofile_or_404(slug)

    response = {
        'success': True,
    }

    if profile not in request.user.profile.subscriptions.all():
        profile.subscribers.add(request.user.profile)
        response['action'] = 'add'
        notifications.send_subscribe_notification(profile, request.user.profile)
        
        awards.grant_user_followers_awards(user=profile.user)
    else:
        profile.subscribers.remove(request.user.profile)
        notifications.remove_subscribe_notification(profile, request.user.profile)
        response['action'] = 'remove'

    return JsonResponse(response)


def user_followings(request: HttpRequest, slug: str):
    """A view that is responsible for showing a subscription and subscriber lists on GET."""
    profile = profiles.get_userprofile_or_404(slug)

    subscription_list = profile.subscriptions.filter()
    subscriber_list = profile.subscribers.filter()

    context = {'profile': profile,
               'subscriber_list': subscriber_list,
               'subscription_list': subscription_list}

    return render(request, 'users/profile/user_followings.html', context=context)


class UserMediaList(ListView):
    model = ProfileMedia
    template_name = 'users/profile/user_profile_media_list.html'
    context_object_name = 'media_list'

    def get_queryset(self) -> QuerySet[Any]:
        # Get only the visible media of the user that is being checked
        profile = profiles.get_userprofile_or_404(
            self.kwargs["slug"]).user.profile
        return ProfileMedia.objects.filter(profile=profile, is_visible=True)

    def get_context_data(self, **kwargs):
        new_context = super().get_context_data(**kwargs)
        new_context['profile'] = profiles.get_userprofile_or_404(
            self.kwargs["slug"])
        return new_context


class UserMediaDetail(DetailView):
    model = ProfileMedia
    template_name = 'users/profile/user_profile_media_detail.html'
    context_object_name = 'media'


def user_media_upload(request: HttpRequest, slug: str):
    profile = profiles.get_userprofile_or_404(slug)

    if request.user.profile != profile:
        return redirect(reverse("user_media_upload", args=(request.user.profile.slug,)))

    form = forms.UploadMediaForm

    if request.method == 'POST':
        form = forms.UploadMediaForm(request.POST, request.FILES)
        if form.is_valid():
            new_media = form.save(commit=False)
            new_media.profile = profile
            new_media.save()

            awards.grant_user_media_creation_awards(request.user)

            return redirect(reverse('user_media_list', args=(slug,)))
    else:
        form = forms.UploadMediaForm

    context = {
        'page_title': 'Upload Your Picture',
        'form': form,
        'form_action_url': reverse('user_media_upload', args=(slug,)),
    }
    return render(request, 'parts/general_form_page.html', context=context)


def user_media_delete(request: HttpRequest, slug):
    profile: UserProfile = profiles.get_userprofile_or_404(slug)

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
            profile_form = forms.ProfileUpdateForm(
                request.POST, instance=request.user.profile)
            user_form = forms.UserUpdateForm(request.POST, instance=request.user)
            password_change_form = forms.UserPasswordChangeForm()

            if profile_form.is_valid() and user_form.is_valid():
                profile_form.save()
                user_form.save()
                messages.success(
                    request, 'Your profile has been successfully updated.')
                return redirect(reverse('user_page', args=(slug,)))

        elif request.POST['updating'] == 'password':
            # Updating the password
            password_change_form = forms.UserPasswordChangeForm(
                request.POST, instance=request.user)

            # Prepopulate the fields
            profile_form = forms.ProfileUpdateForm(initial={
                "bio": request.user.profile.bio,
                "signing": request.user.profile.signing,
            })
            user_form = forms.UserUpdateForm(initial={
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
        profile_form = forms.ProfileUpdateForm(initial={
            "bio": request.user.profile.bio,
            "signing": request.user.profile.signing,
        })
        user_form = forms.UserUpdateForm(initial={
            'username': request.user.username,
            'email': request.user.email,
        })
        password_change_form = forms.UserPasswordChangeForm()

    context = {'profile_form': profile_form, 'user_form': user_form,
               'password_change_form': password_change_form}

    return render(request, 'users/profile/user_edit_page.html', context)


def refresh_pfp(request: HttpRequest, slug: str):
    profile = profiles.get_userprofile_or_404(slug)

    if profile == request.user.profile:
        # Assure that the user is updating his own PFP
        # Is not necessary, as it is possible to just update the PFP of request.user.profile,
        # but for the sake of possible future modifications and clarity it is made this way.
        try:
            profiles.update_pfp(profile=profile)
            messages.success(
                request, 'Your profile picture has been refreshed.')
        except Exception as exc:
            logger.error(exc, exc_info=True)
            messages.error(
                request, 'An error occured when trying to refresh your profile picture. Please try again later.')
    return redirect(reverse('user_edit', args=[slug]))


class TimelinePage(ListView):
    template_name = 'users/timeline.html'
    context_object_name = 'blogs'

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
        form = forms.UserRegistrationForm(request.POST.dict())
        
        restricter = authentication.AttemptRestricter(request, key_prefix='application',
                                             max_attempts=settings.APPLICATION_ATTEMPTS_MAX,
                                             timeout=settings.APPLICATION_RESTRICTION_TIMEOUT)
        
        # Check if the client has sent too many applications in the recent time
        if restricter.is_restricted():
            messages.info(request, "You have already sent too many applications. Please try again later.")
            context['form'] = forms.UserRegistrationForm(initial=form.data)

            return render(request, 'users/logreg/register_page.html', context=context)
        
        if form.is_valid():
            # Save the User, the Application and Profile instances
            try:
                user: User = authentication.register_user(form)
                tasks.send_registration_confirmation_email.delay(user.pk)

                if settings.APPLICATIONS_APPROVE_AUTOMATICALLY:
                    user.application.status = 1 # In this case, the signal doesn't approve the user automatically
                    user.application.save()  # But calling the `save` method does
                    
                # Increase the number of sent applications
                restricter.increase_attempt_count()
                # Restrict if needed
                restricter.add_restriction_if_needed()
                                            
            except Exception as exc:
                logger.critical(exc, exc_info=True)
                form.add_error(
                    field=None, error='Some unknown error occured. Please try again a bit later.')

            return render(request, 'users/logreg/register_page_confirm.html', context=context)

    elif request.method == 'GET':
        form = forms.UserRegistrationForm()

    context['form'] = form

    return render(request, 'users/logreg/register_page.html', context=context)


@login_not_required
def login_page(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect(reverse('logout_page'))

    context = {}

    if request.method == 'POST':
        form = forms.UserAuthenticationForm(data=request.POST.dict())
        
        restricter = authentication.AttemptRestricter(request, key_prefix='login',
                                             max_attempts=settings.LOGIN_ATTEMPTS_MAX,
                                             timeout=settings.LOGIN_RESTRICTION_TIMEOUT)
        if restricter.is_restricted():
            # Show the error and stop validation. Django will not show validation error,
            # so no security risk is imposed.
            messages.error(request, form.error_messages['login_restricted'])
            context['form'] = forms.UserAuthenticationForm(initial=form.data)

            return render(request, 'users/logreg/login_page.html', context=context)

        # Validate the login information
        if form.is_valid(): 
            user: User = form.get_user()
            login(request, user)
            next_page = request.GET.get('next')
            
            # Superusers without a profile are redirected to admin
            if user.is_superuser:
                try:
                    user.profile
                except ObjectDoesNotExist:
                    next_page = reverse('admin:index')
                
            return redirect(next_page or reverse('index_page'))
        
        else:
            # Get and increase the number of failed login attempts. Set it to 1 if it is the first one
            attempt_count = restricter.increase_attempt_count()
            
            # Restrict login access every Nth attempt and log that
            if restricter.add_restriction_if_needed():
                login_restriction_logger.info(f"The {restricter.user_ip} address was restricted trying to log " \
                    f"into the {form.data.get('username')} account. Total login attempts recently: {attempt_count}")

    elif request.method == 'GET':
        form = forms.UserAuthenticationForm()

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
    
    form_class = forms.PasswordResetEmailForm
    extra_email_context = {'settings': settings}
    

    def post(self, request, *args, **kwargs):
        restricter = authentication.AttemptRestricter(request, 'password_reset',
                                             max_attempts=settings.PASSWORD_RESET_ATTEMPTS_MAX,
                                             timeout=settings.PASSWORD_RESET_RESTRICTION_TIMEOUT,
                                             remember_attempts_for=3600*24)
        
        if restricter.is_restricted():
            messages.info(request, "You requested too many password resets. Please try again later.")
            # Process as the usual GET request futher
            return super().get(request, *args, **kwargs)
        
        # Increases the attempt count no matter if the provided email is valid
        restricter.increase_attempt_count()
        # Restrict the next attempt if needed
        restricter.add_restriction_if_needed()
        
        # Proceed further as usual
        return super().post(request, *args, **kwargs)


class PasswordResetConfirm(SuccessMessageMixin, PasswordResetConfirmView):
    template_name = 'users/logreg/reset_password_confirmation.html'
    success_url = '/'
    success_message = "The password has been successfully reset! Feel free to Log In now."

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('logout_page'))

        return super().dispatch(request, *args, **kwargs)
