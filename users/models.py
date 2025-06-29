from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    user = models.ForeignKey(User)
    username = models.CharField(verbose_name='Minecraft Username')
    bio = models.CharField(verbose_name='Bio', max_length=512, default='')
    signing = models.CharField(verbose_name='Signing', max_length=64, default='')
    
    pfp = models.ImageField(verbose_name='Profile picture')
    
    def __str__(self):
        return f'<{self.username} Profile>'


class ProfileComment(models.Model):
    profile = models.ForeignKey(UserProfile, verbose_name=UserProfile, on_delete=models.CASCADE)
    text = models.CharField(max_length=512)
    is_visible = models.BooleanField(default=False)
    
    def __str__(self):
        return f'<{self.profile.username} Comment: {'not' if self.is_visible else ''} visible>'
    