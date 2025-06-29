from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from users.helpers.mcuser import username_to_mc_uuid

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.CharField('Bio', max_length=512, default='')
    signing = models.CharField('Signing', max_length=64, default='')
    mcuuid = models.UUIDField('Minecraft UUID', editable=False)
    slug = models.SlugField(default='', null=False)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

    def save(self, *args, **kwargs) -> None:
        self.slug = str(self.user.username).lower()
        self.mcuuid = username_to_mc_uuid(self.user.username)  # ? Implement caching as this stage
        return super().save(*args, **kwargs)


class ProfileComment(models.Model):
    profile = models.ForeignKey(UserProfile, verbose_name=UserProfile, on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=512)
    is_visible = models.BooleanField(default=False)
    
    def __str__(self):
        return f'<{self.profile.username} Comment: {'not' if self.is_visible else ''} visible>'
    
    
class ProfileMedia(models.Model):
    
    profile = models.ForeignKey(UserProfile, verbose_name='User Profile', on_delete=models.SET_NULL, null=True)
    image = models.ImageField('Profile Image', upload_to="users/profile_media/")
    title = models.CharField('Profile Media Title', max_length=32)
    type = models.SmallIntegerField('Media Type', default=0) # TODO: implement via models.TextChoices
    # 0: photo, 1: video, 2: url photo, 3: url video
    is_visible = models.BooleanField(default=True)
    

class Award(models.Model):
    name = models.CharField(_("Awards"), max_length=32)
    description = models.CharField(_("Description"), max_length=256)
    picture = models.ImageField(_("Image"), upload_to='awards/')


class UserAward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
    

class Friend(models.Model):
    user = models.ForeignKey(User, verbose_name='The User', related_name='friends', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, verbose_name="The user's friend", on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = _("Friends")
        verbose_name_plural = _("Friendss")

    def __str__(self):
        return self.name


class RegistrationApplication(models.Model):
    """Registration Application model

    Args:
        models (ForeignKey): User instance
        models (CharField): The application text
        models (SmallIntegerField): The application status

    """
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name='application')
    text = models.CharField(_("Text"), max_length=256)
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



    