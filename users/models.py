from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from users.helpers.file_uploading import profile_media_upload
from users.helpers.mcuser import username_to_mc_uuid
from common.models import AbstractComment

class UserProfileManager(models.Manager):
    """User manager class that implements some useful methods"""
    def get_queryset(self):
        return super().get_queryset().filter(user__is_active=True).filter(is_visible=True)


class IsVisibleManager(models.Manager):
    """Manager class that queries only the objects that have a field `is_visible` set to `True`."""
    def get_queryset(self):
        return super().get_queryset().filter(is_visible=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.CharField('Bio', max_length=512, default='', blank=True)
    signing = models.CharField('Signature', max_length=64, default='', blank=True)
    mcuuid = models.UUIDField('Minecraft UUID', editable=False)
    slug = models.SlugField(default='', null=False)
    pfp = models.ImageField('Profile picture', upload_to='users/pfps', null=True, blank=True)
    subscriptions = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='subscribers')
    
    is_visible = models.BooleanField('Is profile visible', default=True)
    
    objects: UserProfileManager = UserProfileManager()
    """Model Manager that searches for visible profiles of active users only."""
    all_objects = models.Manager()
    """Model Manager that searches for all the profiles of users."""
    
    
    @property
    def total_blog_likes(self):
        like_count = self.user.blogs.aggregate(likes=models.Count('likes'))['likes']
        return like_count or 0

    def __str__(self):
        return f"{self.user.username}"

    def save(self, *args, **kwargs) -> None:
        if not self._state.adding: 
            # If the user has already been registered before
            return super().save(*args, **kwargs)
            
        self.slug = str(self.user.username).lower()
        self.mcuuid = username_to_mc_uuid(self.user.username)
        return super().save(*args, **kwargs)


class ProfileComment(AbstractComment):
    profile = models.ForeignKey(UserProfile, verbose_name='UserProfile', on_delete=models.SET_NULL, null=True)
    
    
class ProfileMedia(models.Model):
    profile = models.ForeignKey(UserProfile, verbose_name='User Profile', related_name='media_list', on_delete=models.SET_NULL, null=True)
    image = models.ImageField('Profile Image', upload_to=profile_media_upload)
    title = models.CharField('Profile Media Title', max_length=32, null=True, blank=True)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects: IsVisibleManager = IsVisibleManager()
    """Model Manager that searches for visible profile media."""
    all_objects = models.Manager()
    """Model Manager that searches for all profile media."""
    
    @property
    def type(self):
        return 'ProfileMedia'
    

class AwardType(models.Model):
    name = models.CharField(_("Award Type"), max_length=32)
    description = models.CharField(_("Description"), max_length=256)
    picture = models.ImageField(_("Image"), upload_to='awards/')
    code = models.CharField('The Award Type code', max_length=64)
    
    def __str__(self) -> str:
        return f"'{self.name}' Award"


class UserAward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='awards')
    type = models.ForeignKey(AwardType, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f"{self.user.username}'s Award: {self.type.name}"


class Notification(models.Model):
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    text = models.CharField(_("Text"), max_length=512)
    is_seen = models.BooleanField(_("Is seen"), default=False)
    is_deleted = models.BooleanField(_("Is deleted"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    identifier = models.CharField(_('Identifier'), max_length=128)
    """A string that can be used to quickly find the notification. Should have the
    following format: "`action;arg1:value;arg2:value;...;`\""""
    
    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")

    def __str__(self):
        return f'<{self.user.username} Notification>'

    
class RegistrationApplication(models.Model):
    """Registration Application model

    Args:
        models (ForeignKey): User instance
        models (CharField): The application text
        models (SmallIntegerField): The application status

    """
       
    APPLICATION_STATUSES = {
        0: 'Not Reviewed',
        1: 'Approved',
        2: 'Rejected'
    }
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name='application', blank=True)
    text = models.CharField(_("Text"), max_length=256, blank=True)
    status = models.SmallIntegerField('Application status', default=0, choices=APPLICATION_STATUSES)
    was_ever_reviewed = models.BooleanField('Was the Application ever reviewed?', default=False)

    class Meta:
        verbose_name = _("Application")
        verbose_name_plural = _("Applications")

    def __str__(self):
        if self.user:
            return f"{self.user.username}'s Application"
        else:
            return "Deleted user's Application"
