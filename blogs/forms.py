from django import forms
import common.forms
from . import models
from django_ckeditor_5.fields import CKEditor5Widget
from django.utils.html import strip_tags

class BlogEditForm(forms.ModelForm):
    
    class Meta:
        model = models.Blog
        fields = ('title', 'section', 'text')
        widgets = {
              "text": CKEditor5Widget(
                  attrs={"class": "django_ckeditor_5"}, config_name="extends"
              )
          }
        
    def clean_text(self):
        data = self.cleaned_data['text']
        
        if len(strip_tags(data)) < 30:
            raise forms.ValidationError('The post content should be 30 or more characters long.')
        
        return data


class BlogCommentCreationForm(common.forms.AbstractCommentCreationForm):
    class Meta(common.forms.AbstractCommentCreationForm.Meta):
        model = models.BlogComment
