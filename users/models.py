from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from users.helpers.mcuser import username_to_mc_uuid

class UserManager(models.Manager):
    """User manager class that implements some useful methods.
    """
    def subscribers(self, of_user):
        """A handy method that returns the queryset of Users that are subscribers of the `of_user` User.

        Args:
            of_user (UserProfile): An instance of the user profile

        Returns:
            QuerySet: set of Users that are subscribed to the `of_user` User.
        """
        return self.filter(subscriptions__id=of_user.pk)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.CharField('Bio', max_length=512, default='', blank=True)
    signing = models.CharField('Signing', max_length=64, default='', blank=True)
    mcuuid = models.UUIDField('Minecraft UUID', editable=False)
    slug = models.SlugField(default='', null=False)
    pfp = models.ImageField('Profile picture', upload_to='pfps', null=True, blank=True)
    subscriptions = models.ManyToManyField('self', blank=True, symmetrical=False)
    
    objects = UserManager()

    def __str__(self):
        return f"{self.user.username}"

    def save(self, *args, **kwargs) -> None:
        self.slug = str(self.user.username).lower()
        self.mcuuid = username_to_mc_uuid(self.user.username)  # ? Implement caching as this stage
        return super().save(*args, **kwargs)


class ProfileComment(models.Model):
    profile = models.ForeignKey(UserProfile, verbose_name='UserProfile', on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=512)
    is_visible = models.BooleanField(default=False)
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'<{self.profile.user.username} Comment: {'not' if self.is_visible else ''} visible>'
    
    
class ProfileMedia(models.Model):
    profile = models.ForeignKey(UserProfile, verbose_name='User Profile', related_name='media_list', on_delete=models.SET_NULL, null=True)
    image = models.ImageField('Profile Image', upload_to="users/profile_media/")
    title = models.CharField('Profile Media Title', max_length=32, null=True)
    type = models.SmallIntegerField('Media Type', default=0) # TODO: implement via models.TextChoices
    # 0: photo, 1: video, 2: url photo, 3: url video
    is_visible = models.BooleanField(default=True)
    

class Award(models.Model):
    name = models.CharField(_("Awards"), max_length=32)
    description = models.CharField(_("Description"), max_length=256)
    picture = models.ImageField(_("Image"), upload_to='awards/')


class UserAward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='awards')
    award = models.ForeignKey(Award, on_delete=models.CASCADE)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(_("Text"), max_length=128)
    is_seen = models.BooleanField(_("Is seen"))
    is_deleted = models.BooleanField(_("Is deleted"))

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")

    def __str__(self):
        return f'<{self.user.profile.username} Notification>'
    

# class Friend(models.Model):
#     user = models.ForeignKey(User, verbose_name='The User', related_name='friends', on_delete=models.CASCADE)
#     friend = models.ForeignKey(User, verbose_name="The user's friend", on_delete=models.CASCADE)
    
#     class Meta:
#         verbose_name = _("Friend")
#         verbose_name_plural = _("Friends")

#     def __str__(self):
#         return f"{self.user.username}'s friend: {self.friend.username}"


class RegistrationApplication(models.Model):
    """Registration Application model

    Args:
        models (ForeignKey): User instance
        models (CharField): The application text
        models (SmallIntegerField): The application status

    """
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name='application')
    text = models.CharField(_("Text"), max_length=256, blank=True)
    status = models.SmallIntegerField('Application status', default=0) # TODO: implement via models.TextChoices
    # 0: not reviewed, 1: approved, 2: denied

    class Meta:
        verbose_name = _("Application")
        verbose_name_plural = _("Applications")

    def __str__(self):
        if self.user:
            return f"{self.user.username}'s Application"
        else:
            return "Deleted user's Application"
