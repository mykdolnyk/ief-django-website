from django.urls import path
from . import views


urlpatterns = [
    path('', views.user_list, name='user_list'),
    path("user/<int:id>/", views.user_page, name="user_page"),
    path("user/<int:id>/edit/", views.user_edit, name="user_edit"),
    path("user/<int:id>/awards/", views.user_award_list, name="user_award_list"),
    path("user/<int:id>/friends/", views.user_friend_list, name="user_friend_list"),
    path("user/<int:id>/media/", views.user_media_list, name="user_media_list"),
    path("user/<int:id>/posts/", views.user_post_list, name="user_post_list"),
    path("user/notifications/", views.user_notifications, name="user_notifications"),
]
