from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment, Follow
from yatube.settings import POST_ON_PAGE


def pagination(request, post_list):
    paginator = Paginator(post_list, POST_ON_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(20, key_prefix="index_page")
def index(request):
    post_list = Post.objects.select_related("group")
    page_obj = pagination(request=request, post_list=post_list)
    context = {
        "page_obj": page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = pagination(request=request, post_list=post_list)
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    page_obj = pagination(request=request, post_list=author.posts.all())
    following = Follow.objects.filter(author=author)
    context = {
        "page_obj": page_obj,
        "author": author,
        "following": following
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.select_related('post')
    form = CommentForm(request.POST or None)
    context = {
        "post": post,
        "form": form,
        "comments": comments
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(
            request.POST or None,
            files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author.username)
    form = PostForm()
    context = {
        "form": form,
        "is_edit": False
    }
    return render(request, "posts/create_post.html", context)


def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect("posts:post_detail", post_id)
    form = PostForm(
        request.POST or None,
        instance=post,
        files=request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id)
    context = {
        "form": form,
        'is_edit': True,
        "post": post,
    }
    return render(request, "posts/create_post.html", context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    author_querry = Follow.objects.filter(user=request.user)
    author_values_list = author_querry.values_list('author')
    post_list = Post.objects.filter(author_id__in=author_values_list)
    page_obj = pagination(request=request, post_list=post_list)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if Follow.follow_can_be_created(request.user, author):
        Follow.objects.create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = get_object_or_404(Follow, author=author)
    follow.delete()
    return redirect(f'/profile/{username}')
