from django.contrib.auth.models import User
from django.template.loader import render_to_string

from users.models import Notification, ProfileComment, UserProfile
from blogs.models import Blog, BlogComment


like_identifier_template = "user_like_blog;user_pk:{user_pk};blog_pk:{blog_pk};"
subscribe_identifier_template = "user_subscribe;from_profile_pk:{from_profile_pk};to_profile_pk:{to_profile_pk};"
new_blog_identifier_template = "blog_new_post;user_pk:{user_pk};blog_pk:{blog_pk};"


def send_like_notification(liked_blog: Blog, liking_user: User):
    # For every user who liked the post in this signal
    notification_identifier = like_identifier_template.format(user_pk=liking_user.pk,
                                                              blog_pk=liked_blog.pk)
    try:
        Notification.objects.get(identifier=notification_identifier)
        # Don't create the same notification if it already exists.
    except Notification.DoesNotExist:
        text = render_to_string('users/notifications/snippets/user_liked_blog.html',
                                {'liking_user': liking_user,
                                 'blog': liked_blog})
        # Send a notification to the user whos blog was liked
        Notification.objects.create(user=liked_blog.author,
                                    text=text,
                                    identifier=notification_identifier)


def remove_like_notification(liked_blog: Blog, liking_user: User):
    notification_identifier = like_identifier_template.format(user_pk=liking_user.pk,
                                                              blog_pk=liked_blog.pk)
    try:
        Notification.objects.get(identifier=notification_identifier).delete()
    except Notification.DoesNotExist:
        pass


def send_subscribe_notification(subscribed_to_profile: UserProfile, subscribing_profile: UserProfile):
    notification_identifier = subscribe_identifier_template.format(from_profile_pk=subscribing_profile.pk,
                                                                   to_profile_pk=subscribed_to_profile.pk)

    try:
        Notification.objects.get(identifier=notification_identifier)
        # Don't create the same notification if it already exists.
    except Notification.DoesNotExist:
        text = render_to_string('users/notifications/snippets/user_subscribed.html',
                                {'subscribing_profile': subscribing_profile})
        # Send a notification to the user who was subscribed to
        Notification.objects.create(user=subscribed_to_profile.user,
                                    text=text,
                                    identifier=notification_identifier)


def remove_subscribe_notification(subscribed_to_profile: UserProfile, subscribing_profile: UserProfile):
    notification_identifier = subscribe_identifier_template.format(from_profile_pk=subscribing_profile.pk,
                                                                   to_profile_pk=subscribed_to_profile.pk)
    try:
        Notification.objects.get(identifier=notification_identifier).delete()
    except Notification.DoesNotExist:
        pass


def on_new_blog(sender, instance: Blog, created: bool, raw: bool, **kwargs):
    if (not created) or raw:
        # In case the blog is loaded from the fixture or just edited
        return None

    identifier_template = "blog_new_post;user_pk:{user_pk};blog_pk:{blog_pk};"
    # user_pk corresponds to the user who was subscribed to the author of the blog
    blog_author: User = instance.author
    subscribers = blog_author.profile.subscribers

    text = render_to_string(
        'users/notifications/snippets/blog_new_post.html', {'blog': instance})

    identifier_template = identifier_template.format(
        blog_pk=instance.pk, user_pk='{user_pk}')

    for subscriber in subscribers.all():
        notification_identifier = identifier_template.format(
            user_pk=subscriber.pk)

        Notification.objects.create(
            user=subscriber.user,
            text=text,
            identifier=notification_identifier
        )


def send_comment_notification(comment: ProfileComment | BlogComment):

    if isinstance(comment, ProfileComment):

        identifier_template = "user_commented_profile;from_profile_pk:{from_profile_pk};to_profile_pk:{to_profile_pk};"
        notification_identifier = identifier_template.format(from_profile_pk=comment.owner.profile.pk,
                                                             to_profile_pk=comment.profile.pk)

        template_path = 'users/notifications/snippets/user_commented_profile.html'
        receiving_user = comment.profile.user

    elif isinstance(comment, BlogComment):

        identifier_template = "user_commented_blog;from_profile_pk:{from_profile_pk};to_profile_pk:{to_profile_pk};"
        notification_identifier = identifier_template.format(from_profile_pk=comment.owner.profile.pk,
                                                             to_profile_pk=comment.blog.author.pk)

        template_path = 'users/notifications/snippets/user_commented_blog.html'
        receiving_user = comment.blog.author

    else:
        raise ValueError

    text = render_to_string(template_path, {'comment': comment})
    Notification.objects.create(
        user=receiving_user,
        text=text,
        identifier=notification_identifier)
