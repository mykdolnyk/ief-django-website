import logging
from django.contrib.auth.models import User
from django.http import Http404, HttpRequest
from users import tasks
from users.models import RegistrationApplication, UserProfile
from users.helpers import mcuser
from django.core.files.base import ContentFile
from .awards import grant_award
from django.core.cache import cache
from .profiles import update_pfp

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
    grant_award(user, 'user_approved_1')

    user.application.was_ever_reviewed = True

    user.save()
    
    tasks.send_application_approval_email.delay(user.pk)
    
    info_to_log = user.__dict__.copy()
    info_to_log.pop('password')
    
    logger.info(f'The following user was approved:\n{info_to_log}')


def reject_application(user: User):
    tasks.send_application_rejection_email.delay(user.pk)
    user.application.was_ever_reviewed = True


def get_ip_address(request) -> str:
    """Gets the IP address from the HttpRequest object and returns it as a string."""
    ip: str
    
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        ip = x_forwarded.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
        
    return ip

class AttemptRestricter:
    def __init__(self, request: HttpRequest, key_prefix: str, max_attempts: int, timeout: int,
                 remember_attempts_for: int = 3600*12):
        """Object made for keeping track of action attempts and restrictions.

        Args:
            request (HttpRequest): Django HttpRequest object.
            key_prefix (str): Prefix that will be used id cache keys like `prefix`_attempts.
            max_attempts (int): Max attempts until the restriction can added.   
            timeout (int): Period of time for which further attempts are restricted
            remember_attempts_for (int, optional): Time for which the attempt count will be cached. Defaults to 43200.
        """
        self.user_ip = get_ip_address(request)
        self.key_prefix: str = key_prefix
        self.max_attempts: int = max_attempts
        self.restriction_timeout: int = timeout
        self.attempts_timeout: int = remember_attempts_for
    
    def is_restricted(self) -> bool:
        """Check if the IP address is restricted. Returns `True`/`False`."""
        return cache.get(f'{self.key_prefix}_restricted:{self.user_ip}', default=False)
        
    def increase_attempt_count(self):
        """Increase the number of action attempts made. Set it to `1` if it is the first one."""
        try:
            self.action_attempts = cache.incr(f'{self.key_prefix}_attempts:{self.user_ip}', 1)
            
        except ValueError:
            cache.set(f'{self.key_prefix}_attempts:{self.user_ip}', 1, self.attempts_timeout)
            self.action_attempts = 1
            
        return self.action_attempts
        
    def add_restriction_if_needed(self) -> bool:
        """If the attempt count is bigger than the max attempt number, adds the restriction
        and returns `True`. Does nothing and returns `False` otherwise."""
        if self.action_attempts % self.max_attempts == 0:
            cache.set(f'{self.key_prefix}_restricted:{self.user_ip}', 
                      value=True, 
                      timeout=self.restriction_timeout)
            return True
        return False
    
    def reset_attempt_count(self):
        cache.delete(f'{self.key_prefix}_attempts:{self.user_ip}')
    
    def manually_remove_restriction(self):
        cache.delete(f'{self.key_prefix}_restricted:{self.user_ip}')
