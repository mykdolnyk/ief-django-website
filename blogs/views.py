from django.http import HttpRequest
from django.shortcuts import render

# Create your views here.


def blog_list(request: HttpRequest):
    pass


def blog_section(request: HttpRequest, section: int):
    pass


def blog_page(request: HttpRequest, section: int, id: int):
    pass


def blog_edit(request: HttpRequest, section: int, id: int):
    pass


def blog_create(request: HttpRequest):
    pass