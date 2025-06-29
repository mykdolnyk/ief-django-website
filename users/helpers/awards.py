from django.contrib.auth.models import User
from blogs.models import Blog, BlogComment
from helpers.models import AbstractComment
from users.models import AwardType, Notification, ProfileComment

def grant_award(user:User, award_type_code:str, silent:bool=False):
    """A function that creates an UserAward object if the corresponding AwardType exists, and
    sends a notification to the user if needed.
    If the user already has such an award, it doesn't get created, and the function returns
    `False`. If the award was created successfully, returns `True`."""
    type_of_new_award: AwardType = AwardType.objects.get(code=award_type_code)
    
    for award in user.awards.all():
        if award.type == type_of_new_award:
            # If the user already has this award
            return False

        user.awards.create(type=type_of_new_award)
        
        if not silent:
            Notification.objects.create(
            user=user,
            text=f'You received a new award: <b>{type_of_new_award.name}</b>! Go check it out in your profile.')
            
        return True
            
    else: 
        raise ValueError('There is no AwardType with such code.')


def grant_blog_creation_awards(user: User):
    blog_count = user.blogs.count()

    match blog_count:
        case 1:
            grant_award(user, 'blog_first_post')
        case 5:
            grant_award(user, 'blog_5th_post')
        case 20:
            grant_award(user, 'blog_20th_post')
        case 50:
            grant_award(user, 'blog_50th_post')
        case 100:
            grant_award(user, 'blog_100th_post')


def grant_blog_likes_awards(user: User):
    like_count = user.profile.total_blog_likes

    match like_count:
        case 1:
            grant_award(user, 'blog_first_like')
        case 5:
            grant_award(user, 'blog_5th_like')
        case 20:
            grant_award(user, 'blog_20th_like')
        case 50:
            grant_award(user, 'blog_50th_like')
        case 100:
            grant_award(user, 'blog_100th_like')


def grant_user_followers_awards(user: User):
    follower_count = user.profile.subscribers.count()
    total_users_count = User.objects.all().count()

    match follower_count:
        case 1:
            grant_award(user, 'user_first_follower')
        case 5:
            grant_award(user, 'user_5th_follower')
        case 10:
            grant_award(user, 'user_10th_follower')
            
    """Check if all users were subscribed"""
    if follower_count == total_users_count:
        grant_award(user, 'user_every_follower')
        

def grant_user_media_creation_awards(user: User):
    media_count = user.media_list.count()

    match media_count:
        case 1:
            grant_award(user, 'user_first_media')
        case 5:
            grant_award(user, 'user_5th_media')
        case 10:
            grant_award(user, 'user_10th_media')


def grant_user_comment_creation_awards(user: User):
    user_commment_count = BlogComment.objects.filter(owner=user).count()
    blog_commment_count = ProfileComment.objects.filter(owner=user).count()
    
    total_comment_count = user_commment_count + blog_commment_count

    match total_comment_count:
        case 1:
            grant_award(user, 'user_first_comment')
        case 10:
            grant_award(user, 'user_10th_comment')
        case 25:
            grant_award(user, 'user_25th_comment')
