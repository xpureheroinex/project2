from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (ListView, DetailView, TemplateView)
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from .models import Group, Membership, Post
from .forms import GroupForm, PostForm
from django.utils import timezone
from django.template.response import TemplateResponse


import pdb


def home_page(request):
    return render(request, template_name='homepage.html')

def user_login(request):
    if request.method == "GET":
        return render(request, template_name='login.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                return render(request, 'login.html', {'error': settings.LOGIN_ERROR_MESSAGE}, status=401)
                # return HttpResponse(settings.LOGIN_ERROR_MESSAGE, status=401)
                # return TemplateResponse(request, 'login.html',
                #                     context={'error': settings.LOGIN_ERROR_MESSAGE},
                #                     status=400)
        except User.DoesNotExist:
            return HttpResponse(settings.LOGIN_ERROR_MESSAGE, status=401)

def user_logout(request):
    user = request.user
    logout(user)
    return HttpResponseRedirect('/')

def user_registration(request):
    if request.method == "GET":
        return render(request, template_name='registration.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        try:
            user = User.objects.get(username=username)
            return HttpResponse(settings.REGISTRATION_USER_EXISTS_ERROR_MESSAGE,
                                status=400)
        except User.DoesNotExist:
            if password1 == password2:
                user = User.objects.create_user(username, email)
                user.set_password(password1)
                return HttpResponseRedirect('/')
            else:
                return HttpResponse(settings.REGISTRATION_PASSWORDS_ERROR_MESSAGE,
                                    status=400)


class GroupsList(LoginRequiredMixin, ListView):

    model = Group
    template_name = 'groups/groups_list.html'


class GroupInfo(LoginRequiredMixin, DetailView):

    model = Group
    template_name = 'groups/group_info.html'


class GroupCreate(LoginRequiredMixin, TemplateView):

    def get(self, request):
        template_name = "groups/group_form.html"
        return render(request, template_name=template_name)

    def post(self, request):
        name = request.POST.get('name')
        theme = request.POST.get('theme')
        creator = request.user
        data = {'name': name,
                'theme': theme,
                'creator': creator.pk}
        form = GroupForm(data)
        if form.is_valid():
            group = form.instance
            group.save()
            return HttpResponseRedirect('/groups/')
        return HttpResponse("Data is not valid", status=400)


class GroupUpdate(LoginRequiredMixin, TemplateView):

    def get(self, request, group_id):
        group = Group.objects.get(pk=group_id)
        form = GroupForm(instance=group)
        template_name = "groups/group_form.html"
        return render(request, template_name, {'form': form})

    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        name = request.POST.get('name')
        theme = request.POST.get('theme')
        data = {'name': name, 'theme': theme, 'creator': group.creator.pk}
        form = GroupForm(data=data, instance=group)
        if form.is_valid():
            form.save()
            # return render(request, "groups/group_info.html")
            return HttpResponseRedirect(f'/groups/{group_id}/')
        return HttpResponse("Update wasn't successful", status=400)


class GroupDelete(LoginRequiredMixin, TemplateView):
    template_name = 'groups/group_form.html'

    def post(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id)
        try:
            group.delete()
            return HttpResponseRedirect('/groups/')
        except:
            return HttpResponse("Couldn't delete", status=400)


class GroupJoin(LoginRequiredMixin, TemplateView):

    def post(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id)
        user = request.user
        try:
            membership = Membership.objects.get(group=group, user=user)
            membership.delete()
        except Membership.DoesNotExist:
            Membership.objects.create(group=group, user=user, date_joined=timezone.now())

        return HttpResponseRedirect(f'/groups/')


class PostsList(LoginRequiredMixin, ListView):

    model = Post
    template_name = 'posts/posts_list.html'

class PostInfo(LoginRequiredMixin, DetailView):

    model = Post
    template_name = 'posts/post_info.html'

class PostCreate(LoginRequiredMixin, TemplateView):

    def get(self, request):
        template_name = 'posts/post_form.html'
        return redirect(request, template_name=template_name)

    def post(self, request):
        title = request.POST.get('title')
        text = request.POST.get('text')
        creator = request.user
        data = {'title': title,
                'text': text,
                'creator': creator.pk}
        form = PostForm(data)
        if form.is_valid():
            post = form.instance
            post.save()
            return HttpResponseRedirect('/posts/')
        return HttpResponse("Couldn't create a post", status=400)

class PostUpdate(LoginRequiredMixin, TemplateView):

    def get(self, request):
        template_name = 'posts/post_form.html'
        return render(request, template_name=template_name)

    def post(self, request, post_id):
        title = request.POST.get('title')
        text = request.POST.get('text')
        post = get_object_or_404(Post, pk=post_id)
        data = {'title': title, 'text': text, 'creator': post.creator.pk}
        form = PostForm(data=data, instance=post)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(f'/posts/{post_id}')
        return HttpResponse("Update wasn't successful", status=400)

class PostDelete(LoginRequiredMixin, TemplateView):

    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        try:
            post.delete()
            return HttpResponseRedirect('/posts/')
        except:
            return HttpResponse("Couldn't delete", status=400)










