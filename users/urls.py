from django.urls import path
from . import views


urlpatterns = [
    path('', views.UserListView.as_view(), name='user_list'),
    path("notifications/", views.user_notifications, name="user_notifications"), # 'Notifications' user is not welcome :(
    path("<slug:slug>/", views.user_page, name="user_page"),
    path("<slug:slug>/edit/", views.user_edit, name="user_edit"),
    path("<slug:slug>/awards/", views.user_award_list, name="user_award_list"),
    path("<slug:slug>/friends/", views.user_friend_list, name="user_friend_list"),
    path("<slug:slug>/media/", views.user_media_list, name="user_media_list"),
    path("<slug:slug>/posts/", views.user_post_list, name="user_post_list"),
]
