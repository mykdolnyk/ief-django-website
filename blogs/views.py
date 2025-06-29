from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import random
from django.contrib import messages
from django.db.models import Count

from blogs.forms import BlogCommentCreationForm, BlogEditForm
from users.models import ProfileMedia, UserProfile
from .models import Blog, BlogComment, Section

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic import TemplateView

@login_required(login_url=settings.LOGIN_PAGE_NAME)
def index_page(request: HttpRequest):
    # Get Top 3 users by Blog count
    top_players = UserProfile.objects.annotate(count=Count('user__blogs')).order_by('-count')[:3]
    
    # Get a random sight's ID and then get the object.
    sight_ids = Blog.objects.filter(section__slug='sights').values_list('pk', flat=True)

    if sight_ids:
        random_sight_id = random.choice(sight_ids)
        sight = Blog.objects.get(pk=random_sight_id)
    else:
        sight = None

    # Get random blogs' IDs and then get the objects.
    blog_ids = list(Blog.objects.values_list('pk', flat=True))
    
    sample_size = 3 # The number of blogs shown on the Index page 
    if len(blog_ids) >= sample_size:
        random_blog_ids = random.sample(blog_ids, sample_size)
    else:
        # If the sample is larger than population of the Blog objects
        random_blog_ids = blog_ids
    
    blog_list = Blog.objects.filter(pk__in=random_blog_ids)
    
    
    context = {
        'top_players': top_players,
        'sight': sight,
        'blog_list': blog_list,
        'admin_message': 'hi im a blgolblogfdg i am a good bou'
        }
    
    return render(request, 'blogs/index_page.html', context=context)


@login_required(login_url=settings.LOGIN_PAGE_NAME)
def blog_list(request: HttpRequest):
    context = {
        'sections': Section.objects.filter(),
        'blogs': Blog.objects.filter().order_by('-created_at'),
    }
    
    return render(request, 'blogs/blog_list.html', context=context)


@login_required(login_url=settings.LOGIN_PAGE_NAME)
def blog_section(request: HttpRequest, section: str):
    context = {
        'sections': Section.objects.filter(),
        'blogs': Blog.objects.filter(section__slug=section).order_by('-created_at'),
        'current_section': Section.objects.get(slug=section),
    }
    
    return render(request, 'blogs/blog_section.html', context=context)


@login_required(login_url=settings.LOGIN_PAGE_NAME)
def blog_page(request: HttpRequest, section: str, blog: str):
    context = {
        'blog': get_object_or_404(Blog, slug=blog),
        'comments': BlogComment.displayed_objects.filter(blog__slug=blog),
        'comment_form': BlogCommentCreationForm()
    }
    
    return render(request, 'blogs/blog_page.html', context=context)


@login_required(login_url=settings.LOGIN_PAGE_NAME)
def blog_create_comment(request: HttpRequest, section: str, blog: str):
    if request.method != 'POST':   
        return HttpResponseNotAllowed()

    blog_instance = get_object_or_404(Blog, slug=blog)
    
    form = BlogCommentCreationForm(request.POST)
    
    if form.is_valid():
        new_comment: BlogComment = form.save(commit=False)
        
        new_comment.blog = blog_instance # The comment is created on the blog that is was written on
        new_comment.is_visible = True # It is set to be visible
        new_comment.owner = request.user # The owner of the comment is the request user

        new_comment.save()
        
    return redirect(reverse('blog_page', args=(section, blog,)))


@login_required(login_url=settings.LOGIN_PAGE_NAME)
def blog_like(request: HttpRequest, section: str, blog: str):
    blog_instance: Blog = get_object_or_404(Blog, slug=blog)
    
    response = {
        'success': True,
    }
    
    if blog_instance not in request.user.liked_blogs.all():
        blog_instance.likes.add(request.user)
        response['action'] = 'add'
    else:
        blog_instance.likes.remove(request.user)
        response['action'] = 'remove'
        
    return JsonResponse(response)


@login_required(login_url=settings.LOGIN_PAGE_NAME)
def blog_edit(request: HttpRequest, section: str, blog: str):
    # ! Prevent other users from accessing the views (either hardcode
    # ! one user or use permissions)
    
    blog_instance: Blog = get_object_or_404(Blog, slug=blog)
    
    if request.method == "POST":
        form = BlogEditForm(request.POST, instance=blog_instance)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Your post has been updated successfully.')
            return redirect(reverse('blog_page', args=(section, blog,)))

    elif request.method == "GET":
        form = BlogEditForm(instance=blog_instance)
        
    context = {'form': form,
               'page_title': 'Update Your Existing Post'}
    
    return render(request, 'blogs/blog_edit_page.html', context)


@login_required(login_url=settings.LOGIN_PAGE_NAME)
def blog_create(request: HttpRequest):
    if request.method == "POST":
        form = BlogEditForm(request.POST)
        
        if form.is_valid():
            blog: Blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            grant_blog_awards(user=request.user, blog=blog)
            return redirect(reverse('blog_page', args=(blog.section.slug, blog.slug,)))

    elif request.method == "GET":
        form = BlogEditForm()
        
    context = {'form': form,
               'page_title': 'Make a New Post'}
    
    return render(request, 'blogs/blog_edit_page.html', context)


class AllMediaList(LoginRequiredMixin, ListView):
    model = ProfileMedia
    context_object_name = 'media_list'
    template_name = 'blogs/all_profile_media_list.html'
    login_url = settings.LOGIN_PAGE_NAME


class AboutPage(LoginRequiredMixin, TemplateView):
    template_name = 'blogs/about.html'
    login_url = settings.LOGIN_PAGE_NAME
    
# ------------------ HTTP Error Handlers ------------------

def handle_404(request: HttpRequest, exception=None):
    context = {
        'exception': exception,
        'status': 404,
        'description': 'Such page doesn\'t exist.'
    }
    return render(request, 'general/error_page.html', context=context, status=context['status'])
    
def handle_500(request: HttpRequest, exception=None):
    context = {
        'exception': exception,
        'status': 500,
        'description': 'There was some error on the side of the server.'
    }
    return render(request, 'general/error_page.html', context=context, status=context['status'])

def handle_403(request: HttpRequest, exception=None):
    context = {
        'exception': exception,
        'status': 403,
        'description': 'Permission Denied.'
    }
    return render(request, 'general/error_page.html', context=context, status=context['status'])

def handle_400(request: HttpRequest, exception=None):
    context = {
        'exception': exception,
        'status': 400,
        'description': 'Bad Request.'
    }
    return render(request, 'general/error_page.html', context=context, status=context['status'])
