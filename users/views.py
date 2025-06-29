from django.http import HttpRequest
from django.shortcuts import render

# Create your views here.

def user_list(request: HttpRequest):
    pass


def user_page(request: HttpRequest, id: int):
    pass


def user_award_list(request: HttpRequest, id: int):
    pass


def user_friend_list(request: HttpRequest, id: int):
    pass


def user_media_list(request: HttpRequest, id: int):
    pass


def user_post_list(request: HttpRequest, id: int):
    pass


def user_edit(request: HttpRequest, id: int):
    pass


def user_notifications(request: HttpRequest):
    pass


def login(request: HttpRequest):
    pass


def register(request: HttpRequest):
    pass


def logout(request: HttpRequest):
    pass
