from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .modules import is_follower


def search(request):
    query = request.GET.get('q')
    search_results = Post.objects.filter(text__icontains=query)
    return render(request, 'search_results.html', {'query': query, 'search_results': search_results})


# class SearchResultsView(ListView):
#     model = Post
#     template_name = 'search_results.html'

#     def get_queryset(self):
#         query = self.request.GET.get('q')
#         object_list = Post.objects.filter(text__icontains=query)
#         return object_list


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
    }
    return render(request, 'index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_posts = group.posts.all()
    paginator = Paginator(group_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'group': group,
        'page': page,
    }
    return render(request, 'group.html', context)


@login_required
def new_post(request):
    if request.method != 'POST':
        form = PostForm()
        return render(request, 'new.html', {'form': form})
    form = PostForm(request.POST, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    profile_posts = author.posts.all()
    paginator = Paginator(profile_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        following = is_follower(request.user, author.username)
    return render(request, 'profile.html', {'profile': author,
                                            'posts': profile_posts,
                                            'page': page,
                                            'following': following,
                                            'group': group})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    author = post.author
    current_user = request.user
    user_posts = author.posts.all()
    count = user_posts.count()
    form = CommentForm(request.POST or None)
    comments = author.comments.all()
    context = {'post': post, 'author': author, 'count': count,
               'current_user': current_user, 'form': form,
               'comments': comments, }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if request.user != post.author:
        return redirect('post', username, post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('post', username, post_id)
    return render(request, 'new.html', {'form': form, 'post': post})


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('post', username=username, post_id=post_id)


@login_required
def follow_index(request):
    current_user = request.user
    post_list = Post.objects.filter(author__following__user=current_user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator
    }
    return render(request, 'follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', username=username)


class AddGroupView(CreateView):
    model = Group
    template_name = 'add_group'
    fields = '__all__'
