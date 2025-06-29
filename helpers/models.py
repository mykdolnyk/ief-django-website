from django.db import models
from django.contrib.auth.models import User


class DisplayedCommentsManager(models.Manager):
    """Object Manager that should be used when trying to display the comments."""
    def get_queryset(self):
        return super().get_queryset().filter(is_visible=True).order_by('-created_at')


class AbstractComment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=512)
    is_visible = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects: DisplayedCommentsManager = DisplayedCommentsManager()
    # Queries only visible comments
    all_objects: models.Manager = models.Manager()
    # Queries all comments

    def __str__(self):
        return f"<{self.owner.username}'s Comment: {'not' if not self.is_visible else ''} visible>"

    class Meta:
        abstract = True
