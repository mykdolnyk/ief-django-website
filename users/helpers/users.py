import logging
from django.contrib.auth.models import User
from django.http import Http404
from helpers.email import send_application_approval_email, send_application_rejection_email
from users.models import RegistrationApplication, UserProfile
from users.helpers import mcuser
from django.core.files.base import ContentFile
from .awards import grant_award
from django.core.cache import cache

logger = logging.getLogger(__name__ + '.approve_application')

def register_user(form_data) -> User:
    """A function that takes form as an argument and registers the user. 
    Returns the User instance."""
    try:
        user: User = form_data.save(commit=False) # Save the user from the form to the instance
        user.is_active = False # Make the client inactive until the application is reviewed
        user.save() # Save the user from the instance to the DB (required to get the PK)

        RegistrationApplication.objects.create(
            user = user,
            text = form_data.cleaned_data['application'],
        ).save()
        
        UserProfile.objects.create(
            user=user,
        ).save()
        
    except Exception as exc:
        # In case some error occures, the User instance should be deleted as it was
        # already saved, but the registration failed
        user.delete()
        raise exc # Raise the same exception again for further processing

    return user


def approve_application(user: User):
    update_pfp(user.profile) # Create PFP
    user.is_active = True
    
    # The user gets an Award for being approved:
    grant_award(user, 'user_get_approved')

    user.application.was_ever_reviewed = True

    user.save()
    
    send_application_approval_email(user=user)
    
    info_to_log = user.__dict__.copy()
    info_to_log.pop('password')
    
    logger.info(f'The following user was approved:\n{info_to_log}')


def reject_application(user: User):
    send_application_rejection_email(user=user)
    user.application.was_ever_reviewed = True


def update_pfp(profile: UserProfile, skip_rate_limit=False):
    # TODO: periodical PFP update
    
    if not skip_rate_limit:
        # Check if the PFP was created and updated before...
        pfp_recently_updated = cache.has_key(f"pfp_recently_updated:{profile.user.username}")
        if pfp_recently_updated:
            return None # do nothing
    
    pfp = mcuser.create_pfp(profile.mcuuid)
    pfp = ContentFile(pfp)
    profile.pfp.save(name=f'{profile.slug}.png', content=pfp)
    
    cache.set(f"pfp_recently_updated:{profile.user.username}", True, 60) # Record the PFP Update


def get_userprofile_or_404(slug):
    try:
        profile = UserProfile.objects.get(slug=slug.lower(), user__is_active=True)
    except UserProfile.DoesNotExist:
        raise Http404()
    
    return profile


def get_ip_address(request) -> str:
    """Gets the IP address from the HttpRequest object and returns it as a string."""
    ip: str
    
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        ip = x_forwarded.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
        
    return ip