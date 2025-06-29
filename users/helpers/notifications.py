from django.contrib.auth.models import User
from django.template.loader import render_to_string

from common.models import AbstractComment
from users.models import Notification, ProfileComment, UserProfile
from blogs.models import Blog, BlogComment


def on_like(sender, instance: Blog, action, pk_set, **kwargs):
    """A callback function that is used for the m2m_changed signal."""
    identifier_template = "user_like_blog;user_pk:{user_pk};blog_pk:{blog_pk};"

    if action == 'post_add':
        for user_pk in pk_set:
            # For every user who liked the post in this signal
            notification_identifier = identifier_template.format(user_pk=user_pk,
                                                                 blog_pk=instance.pk)
            liking_user = User.objects.get(pk=user_pk)

            try:
                Notification.objects.get(identifier=notification_identifier)
                # Don't create the same notification if it already exists.

            except Notification.DoesNotExist:
                text = render_to_string('users/notifications/snippets/user_liked_blog.html',
                                        {'liking_user': liking_user,
                                         'blog': instance})

                # Send a notification to the user whos blog was liked
                Notification.objects.create(user=instance.author,
                                            text=text,
                                            identifier=notification_identifier)

    if action == 'post_remove':
        # Remove the notification if the like was removed later on
        for user_pk in pk_set:
            notification_identifier = identifier_template.format(user_pk=user_pk,
                                                                 blog_pk=instance.pk)
            try:
                Notification.objects.get(
                    identifier=notification_identifier).delete()

            except Notification.DoesNotExist:
                pass


def on_subscription(sender, instance: UserProfile, action, pk_set, **kwargs):
    """A callback function that is used for the m2m_changed signal."""
    identifier_template = "user_subscribe;from_profile_pk:{from_profile_pk};to_profile_pk:{to_profile_pk};"

    if action == 'post_add':
        for profile_pk in pk_set:
            # For every user profile which subscribed in this signal
            notification_identifier = identifier_template.format(from_profile_pk=profile_pk,
                                                                 to_profile_pk=instance.user.pk)

            subscribing_profile = UserProfile.objects.get(pk=profile_pk)

            try:
                Notification.objects.get(identifier=notification_identifier)
                # Don't create the same notification if it already exists.

            except Notification.DoesNotExist:
                text = render_to_string('users/notifications/snippets/user_subscribed.html',
                                        {'subscribing_profile': subscribing_profile})
                # Send a notification to the user who was subscribed to
                Notification.objects.create(user=instance.user,
                                            text=text,
                                            identifier=notification_identifier)

    if action == 'post_remove':
        # Remove the notification if the subscription was removed later on
        for profile_pk in pk_set:
            notification_identifier = identifier_template.format(from_profile_pk=profile_pk,
                                                                 to_profile_pk=instance.user.pk)
            try:
                Notification.objects.get(
                    identifier=notification_identifier).delete()

            except Notification.DoesNotExist:
                pass


def on_new_blog(sender, instance: Blog, **kwargs):

    identifier_template = "blog_new_post;user_pk:{user_pk};blog_pk:{blog_pk};"
    # user_pk corresponds to the user who was subscribed to the author of the blog
    blog_author: User = instance.author
    subscribers = blog_author.profile.subscribers

    text = render_to_string(
        'users/notifications/snippets/blog_new_post.html', {'blog': instance})
    
    identifier_template = identifier_template.format(blog_pk=instance.pk, user_pk='{user_pk}')
    
    for subscriber in subscribers.all():
        notification_identifier = identifier_template.format(user_pk=subscriber.pk)

        Notification.objects.create(
            user=subscriber.user,
            text=text,
            identifier=notification_identifier
        )


def notify_about_comment(comment: ProfileComment | BlogComment):
    
    if isinstance(comment, ProfileComment):

        identifier_template = "user_commented_profile;from_profile_pk:{from_profile_pk};to_profile_pk:{to_profile_pk};"
        notification_identifier = identifier_template.format(from_profile_pk=comment.owner,
                                                             to_profile_pk=comment.profile)

        template_path = 'users/notifications/snippets/user_commented_profile.html'
        receiving_user = comment.profile.user

    elif isinstance(comment, BlogComment):

        identifier_template = "user_commented_blog;from_profile_pk:{from_profile_pk};to_profile_pk:{to_profile_pk};"
        notification_identifier = identifier_template.format(from_profile_pk=comment.owner,
                                                             to_profile_pk=comment.blog.author)

        template_path = 'users/notifications/snippets/user_commented_blog.html'
        receiving_user = comment.blog.author

    else:
        raise ValueError

    text = render_to_string(template_path, {'comment': comment})
    Notification.objects.create(
        user=receiving_user,
        text=text,
        identifier=notification_identifier)
