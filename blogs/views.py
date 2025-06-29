from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse

from blogs.forms import BlogCreationForm
from .models import Blog, Section
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
        'blog': Blog.objects.get(slug=blog)
    }
    
    return render(request, 'blogs/blog_page.html', context=context)


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