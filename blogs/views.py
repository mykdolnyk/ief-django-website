from django.conf import settings
from django.http import HttpRequest, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required


from blogs.forms import BlogCommentCreationForm, BlogCreationForm
import users
from .models import Blog, BlogComment, Section
# Create your views here.

def index_page(request: HttpRequest):
    context = {}
    
    return render(request, 'blogs/index_page.html', context=context)


def blog_list(request: HttpRequest):
    context = {
        'sections': Section.objects.filter(),
        'blogs': Blog.objects.filter(),
    }
    
    return render(request, 'blogs/blog_list.html', context=context)


def blog_section(request: HttpRequest, section: str):
    context = {
        'sections': Section.objects.filter().exclude(slug=section),
        'blogs': Blog.objects.filter(section__slug=section),
        'current_section': Section.objects.get(slug=section),
    }
    
    return render(request, 'blogs/blog_section.html', context=context)


def blog_page(request: HttpRequest, section: str, blog: str):
    context = {
        'blog': get_object_or_404(Blog, slug=blog),
        'comments': BlogComment.displayed_objects.filter(blog__slug=blog),
        'comment_form': BlogCommentCreationForm()
    }
    
    return render(request, 'blogs/blog_page.html', context=context)


@login_required(login_url=settings.LOGIN_PAGE_NAME)
def create_comment(request: HttpRequest, section: str, blog: str):
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


def blog_edit(request: HttpRequest, section: str, blog: str):
    pass


def blog_create(request: HttpRequest):
    if request.method == "POST":
        form = BlogCreationForm(request.POST)
        
        if form.is_valid():
            blog: Blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            return redirect(reverse('blog_page', args=(blog.section.slug, blog.slug,)))

    elif request.method == "GET":
        form = BlogCreationForm()
        
    context = {'form': form}
    
    return render(request, 'blogs/blog_create_page.html', context)