from django.urls import path
from . import views


urlpatterns = [
    path("blog/", views.blog_list, name="blog_list"),
    path("blog/<int: section>/", views.blog_section, name="blog_section"),
    path("blog/<int: section>/<int:id>/", views.blog_page, name="blog_page"),
    path("blog/<int: section>/<int:id>/edit", views.blog_edit, name="blog_edit"),
    path("blog/create", views.blog_create, name="blog_create"),
    
]
