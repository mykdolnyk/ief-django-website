from django.urls import path
from . import views


urlpatterns = [
    path("", views.blog_list, name="blog_list"),
    path("<int:section>/", views.blog_section, name="blog_section"),
    path("<int:section>/<int:id>/", views.blog_page, name="blog_page"),
    path("<int:section>/<int:id>/edit", views.blog_edit, name="blog_edit"),
    path("create", views.blog_create, name="blog_create"),
    
]
