from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django import template
from django.db.models import Q
from .models import BlogPost
from .forms import BlogPostForm, UserRegistrationForm
def index(request):
    current_user = request.user
    visible_posts = BlogPost.objects.filter(
        author=current_user)
    return render(request, 'blogapp/index.html', {'posts': visible_posts})

def post_detail(request, post_id):
    post = get_object_or_404(BlogPost, pk=post_id)
    return render(request, 'blogapp/post_detail.html', {'post': post})
def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f'You are now logged in as {username}.')
                return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})
register = template.Library()

@register.filter(name='is_visible')
def is_visible(scheduled_at):
    return scheduled_at <= timezone.now()
def logout_user(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login_user')
@login_required
def create_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # Check if scheduled_at is in the future
            post.save()
            messages.success(request, 'Post scheduled successfully!')
            return redirect('index')
    else:
        form = BlogPostForm()
    return render(request, 'blogapp/create_post.html', {'form': form})
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(BlogPost, pk=post_id)
    if request.method == 'POST':
        form = BlogPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = BlogPostForm(instance=post)
    return render(request, 'blogapp/edit_post.html', {'form': form, 'post': post})
def search_posts(request):
    posts = BlogPost.objects.all()
    query = request.GET.get('q')
    if query:
        # Perform filtering based on the search query
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__username__icontains=query)
        )

    return render(request, 'blogapp/search_results.html', {'posts': posts, 'query': query})
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(BlogPost, pk=post_id)
    post.delete()
    return redirect('index')

