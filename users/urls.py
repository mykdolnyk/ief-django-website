from django.urls import path
from . import views


urlpatterns = [
    path('', views.UserListView.as_view(), name='user_list'),
    path("<slug:slug>/", views.user_page, name="user_page"),
    path("<slug:slug>/edit/", views.user_edit, name="user_edit"),
    path("<slug:slug>/awards/", views.user_award_list, name="user_award_list"),
    path("<slug:slug>/subscribe/", views.user_subscribe, name="user_subscribe"),
    path("<slug:slug>/followings/", views.user_followings, name="user_followings"),
    # path("<slug:slug>/subscriptions/", views.user_subscription_list, name="user_subscription_list"),
    # path("<slug:slug>/subscribers/", views.user_subscriber_list, name="user_subscriber_list"),
    path("<slug:slug>/media/", views.user_media_list, name="user_media_list"),
    path("<slug:slug>/posts/", views.user_post_list, name="user_post_list"),
]
