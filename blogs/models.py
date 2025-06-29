from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

# Create your models here.


class Section(models.Model):
    name = models.CharField(_("Name"), max_length=32)
    
    def __str__(self):
        return self.name


class Blog(models.Model):
    title = models.CharField(_("Title"), max_length=64)
    text = models.CharField(_("Text"), max_length=2048)
    section = models.ForeignKey(Section, verbose_name=_("Section"), on_delete=models.CASCADE)
    author = models.ForeignKey(User, verbose_name=_("Author"), on_delete=models.CASCADE)
    likes = models.IntegerField(_("Like count"))
    
    
class Tag(models.Model):
    title = models.CharField(_("Tag"), max_length=64)
    is_visible = models.BooleanField(default=False)    

    def __str__(self):
        return self.title
    

class BlogTags(models.Model):
    blog = models.ForeignKey(Blog, verbose_name=_("Blog"), on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, verbose_name=_("Tag"), on_delete=models.CASCADE)
    

class BlogComment(models.Model):
    blog = models.ForeignKey(Blog, verbose_name=_("Blog"), on_delete=models.CASCADE)
    text = models.CharField(max_length=512)
    is_visible = models.BooleanField(default=False)
    
    
class BlogMedia(models.Model):
    
    blog = models.ForeignKey(Blog, verbose_name=_("Blog"), on_delete=models.CASCADE)
    image = models.ImageField('Blog Image', upload_to="users/profile_media/")
    title = models.CharField('Blog Media Title', max_length=32)
    type = models.SmallIntegerField('Blog Type', default=0) # TODO: implement via models.TextChoices
    # 0: photo, 1: video, 2: url photo, 3: url video
    is_visible = models.BooleanField(default=True)
