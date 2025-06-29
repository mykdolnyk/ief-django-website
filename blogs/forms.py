from django import forms
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
        fields = ('text', 'section')
        widgets = {
              "text": CKEditor5Widget(
                  attrs={"class": "django_ckeditor_5"}, config_name="extends"
              )
          }


class BlogCommentCreationForm(forms.ModelForm):
    action = forms.CharField(widget=forms.HiddenInput(), initial='create')
    
    class Meta:
        model = models.BlogComment
        fields = ("text",)
        widgets = {
            'text': forms.Textarea()
        }