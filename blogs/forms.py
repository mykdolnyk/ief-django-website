from django import forms
import helpers.forms
from . import models
from django_ckeditor_5.fields import CKEditor5Widget


class BlogCreationForm(forms.ModelForm):
    
    class Meta:
        model = models.Blog
        fields = ('title', 'text', 'section')
        widgets = {
              "text": CKEditor5Widget(
                  attrs={"class": "django_ckeditor_5"}, config_name="extends"
              )
          }
        

class BlogEditForm(forms.ModelForm):
    
    class Meta:
        model = models.Blog
        fields = ('title', 'section', 'text')
        widgets = {
              "text": CKEditor5Widget(
                  attrs={"class": "django_ckeditor_5"}, config_name="extends"
              )
          }


class BlogCommentCreationForm(helpers.forms.AbstractCommentCreationForm):
    class Meta(helpers.forms.AbstractCommentCreationForm.Meta):
        model = models.BlogComment
