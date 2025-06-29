from django.urls import path
from . import views


urlpatterns = [
    path('', views.UserListView.as_view(), name='user_list'),
    path("<slug:slug>/", views.user_page, name="user_page"),
    path("<slug:slug>/edit/", views.user_edit, name="user_edit"),
    path("<slug:slug>/awards/", views.UserAwardList.as_view(), name="user_award_list"),
    path("<slug:slug>/followings/", views.user_followings, name="user_followings"),
    path("<slug:slug>/media/", views.UserMediaList.as_view(), name="user_media_list"),
    path("<slug:slug>/posts/", views.user_post_list, name="user_post_list"),
    
    path("<slug:slug>/subscribe/", views.user_subscribe, name="user_subscribe"),
    path("<slug:slug>/create_comment/", views.create_comment, name="user_create_comment"),
    path("<slug:slug>/refresh_pfp/", views.refresh_pfp, name="user_refresh_pfp"),
    path("<slug:slug>/media/upload/", views.user_media_upload, name="user_media_upload"),
    path("<slug:slug>/media/delete/", views.user_media_delete, name="user_media_delete"),
    
]
