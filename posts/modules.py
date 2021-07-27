from django.shortcuts import get_object_or_404

from .models import User


def is_follower(user, author_username):
    author = get_object_or_404(User, username=author_username)
    return user.follower.filter(author=author).exists()
