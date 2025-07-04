from django.urls import path
from . import views


urlpatterns = [
    path("", views.blog_list, name="blog_list"),
    path("create/", views.blog_create, name="blog_create"),
    path("<slug:section>/", views.blog_section, name="blog_section"),
    path("<slug:section>/<slug:blog>/", views.blog_page, name="blog_page"),
    path("<slug:section>/<slug:blog>/create_comment/", views.blog_create_comment, name="blog_create_comment"),
    path("<slug:section>/<slug:blog>/like/", views.blog_like, name="blog_like"),
    path("<slug:section>/<slug:blog>/edit/", views.blog_edit, name="blog_edit"),
]
