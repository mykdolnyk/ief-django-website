from time import strftime
from typing import Iterable
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
import django_ckeditor_5.fields
from django.utils.text import slugify

from helpers.models import AbstractComment
# Create your models here.


class Section(models.Model):
    name = models.CharField(_("Name"), max_length=32)
    slug = models.SlugField(default='', null=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs) -> None:
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Blog(models.Model):
    title = models.CharField(_("Title"), max_length=64)
    # text = models.CharField(_("Text"), max_length=2048)
    slug = models.SlugField(default='')
    text = django_ckeditor_5.fields.CKEditor5Field(_("Text"), max_length=2048, config_name='extends')    
    section = models.ForeignKey(Section, verbose_name=_("Section"), on_delete=models.CASCADE)
    author = models.ForeignKey(User, verbose_name=_("Author"), on_delete=models.CASCADE, related_name='blogs')
    likes = models.ManyToManyField(User, verbose_name=_("Like count"), related_name='liked_blogs')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs) -> None:
        # Create a slug: first, slugify the title, then
        # replace _ with -. It is needed to prevent creating
        # duplicated slugs. For example: first create "test_1"
        # title, and then create 2 "test" titles.
        new_slug = slugify(self.title).replace('_', '-')
        
        # Check the number of duplicates
        duplicates = Blog.objects.filter(slug=new_slug).count()
        if duplicates > 0:
            # If there is a duplicate, add the number to the slug
            new_slug += f'_{duplicates}'
        self.slug = new_slug
        return super().save(*args, **kwargs)
    
    
class Tag(models.Model):
    title = models.CharField(_("Tag"), max_length=64)
    is_visible = models.BooleanField(default=False)    

    def __str__(self):
        return self.title
    

class BlogTags(models.Model):
    blog = models.ForeignKey(Blog, verbose_name=_("Blog"), on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, verbose_name=_("Tag"), on_delete=models.CASCADE)
    

class BlogComment(AbstractComment):
    blog = models.ForeignKey(Blog, verbose_name='Blog', on_delete=models.SET_NULL, null=True)
    
    
class BlogMedia(models.Model):
    
    blog = models.ForeignKey(Blog, verbose_name=_("Blog"), on_delete=models.CASCADE)
    image = models.ImageField('Blog Image', upload_to="users/profile_media/")
    title = models.CharField('Blog Media Title', max_length=32)
    type = models.SmallIntegerField('Blog Type', default=0) # TODO: implement via models.TextChoices
    # 0: photo, 1: video, 2: url photo, 3: url video
    is_visible = models.BooleanField(default=True)
