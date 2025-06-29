from django import forms

from common import models

class AbstractCommentCreationForm(forms.ModelForm):
    action = forms.CharField(widget=forms.HiddenInput(), initial='create')
    
    class Meta:
        model = models.AbstractComment
        fields = ("text",)
        labels = {
            'text': "Share your thoughts!"
        }
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': "Type here..."})
        }