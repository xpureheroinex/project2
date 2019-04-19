from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (ListView, DetailView, View, TemplateView)
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
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
    logout(request)
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
                user.save()
                return HttpResponseRedirect('/')
            else:
                return HttpResponse(settings.REGISTRATION_PASSWORDS_ERROR_MESSAGE,
                                    status=400)


class GroupsList(LoginRequiredMixin, ListView):

    model = Group
    template_name = 'groups/groups_list.html'


class GroupPage(LoginRequiredMixin, TemplateView):

    def get(self, request, group_id):
        template_name = 'groups/group_info.html'
        group = get_object_or_404(Group, pk=group_id)
        post_list = Post.objects.filter(group=group_id).values()
        posts = [elem for elem in post_list]
        user = request.user
        is_member = self.is_member(user, group)
        is_creator = self.is_creator(user.pk, group_id)
        return render(request, template_name, {'is_member': is_member,
                                               'is_creator': is_creator,
                                               'group': group,
                                               'posts': posts})

    def post(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id)
        user = request.user
        is_member = self.is_member(user, group)
        if is_member:
            membership = Membership.objects.get(group=group, user=user)
            membership.delete()
        else:
            Membership.objects.create(group=group, user=user,
                                      date_joined=timezone.now())
        return HttpResponseRedirect(f'/groups/{group_id}/')


    @staticmethod
    def is_member(user, group):
        try:
            Membership.objects.get(group=group, user=user)
            is_member = True
        except Membership.DoesNotExist:
            is_member = False
        return is_member

    @staticmethod
    def is_creator(user_id, group_id):
        user = User.objects.get(pk=user_id)
        group = Group.objects.get(pk=group_id)
        creator = group.creator
        if creator.pk == user.pk:
            return True
        return False


class GroupCreate(LoginRequiredMixin, TemplateView):

    def get(self, request):
        template_name = "groups/group_create.html"
        form = GroupForm()
        return render(request, template_name, {'form': form})

    def post(self, request):

        name = request.POST.get('name')
        theme = request.POST.get('theme')
        is_private = request.POST.get('private')

        creator = request.user
        data = {'name': name,
                'theme': theme,
                'creator': creator.pk}
        form = GroupForm(data)
        if form.is_valid():
            group = form.instance
            if is_private is None:
                group.save()
            else:
                group.is_private = True
                group.save()
                membership = Membership(user=creator, group=group, date_joined=timezone.now())
                membership.save()
            return HttpResponseRedirect('/groups/')
        return HttpResponse("Data is not valid", status=400)


class GroupUpdate(LoginRequiredMixin, TemplateView):

    def get(self, request, group_id):
        group = Group.objects.get(pk=group_id)
        form = GroupForm(instance=group)
        user = request.user
        template_name = "groups/group_form.html"
        if GroupPage.is_creator(user.pk, group_id):
            return render(request, template_name, {'form': form})
        return render(request, template_name, {'form': form,
                                            'error': "Only creator is allowed to update the group"})

    def post(self, request, group_id):
        user = request.user
        group = get_object_or_404(Group, id=group_id)
        if GroupPage.is_creator(user.pk, group_id):
            name = request.POST.get('name')
            theme = request.POST.get('theme')
            data = {'name': name, 'theme': theme, 'creator': group.creator.pk}
            form = GroupForm(data=data, instance=group)
            if form.is_valid():
                form.save()
                # return render(request, "groups/group_info.html")
                return HttpResponseRedirect(f'/groups/{group_id}/')
        return render(request,  "groups/group_form.html", {'error': "Only creator is allowed to update the group"})


class GroupDelete(LoginRequiredMixin, TemplateView):
    template_name = 'groups/group_form.html'

    def post(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id)
        try:
            group.delete()
            return HttpResponseRedirect('/groups/')
        except:
            return HttpResponse("Couldn't delete", status=400)


@login_required
def invite(request, group_id):
    if request.method == "POST":
        user_current = request.user
        username = request.POST.get('invited_user')
        group = get_object_or_404(Group, pk=group_id)
        is_creator = GroupPage.is_creator(user_current.pk, group.pk)
        data = {'group': group,
                'is_member': True,
                'is_creator': is_creator}
        try:
            user = User.objects.get(username=username)
            try:
                member = Membership.objects.get(user=user, group=group)
                return render(request, 'groups/group_info.html',
                              {**data,'message': "User is a member already"})
            except Membership.DoesNotExist:
                membership = Membership(user=user, group=group, date_joined=timezone.now())
                membership.save()
            return render(request, 'groups/group_info.html', {**data,'message': "User was invited"} )

        except User.DoesNotExist:
            return render(request, 'groups/group_info.html', {**data, 'message': "User doesn't exist",})



# class PostPage(LoginRequiredMixin, TemplateView):
#
#     def get(self, request, **args):
#         template_name = 'posts/posts_list.html'
#
#

class PostsList(LoginRequiredMixin, ListView):

    model = Post
    template_name = 'posts/posts_list.html'

class PostInfo(LoginRequiredMixin, DetailView):

    model = Post
    template_name = 'posts/post_info.html'

class PostCreate(LoginRequiredMixin, TemplateView):

    def get(self, request, group_id):
        template_name = 'posts/post_create.html'
        form = PostForm()
        creator = request.user
        group = get_object_or_404(Group, pk=group_id)
        if GroupPage.is_member(creator, group):
            return render(request, template_name, {'form': form})
        return render(request, 'posts/post_create.html',
                      {'error': "You must join group to create posts"})

    def post(self, request, group_id):
        title = request.POST.get('title')
        text = request.POST.get('text')
        creator = request.user
        publish = request.POST.get('publish')
        group = get_object_or_404(Group, pk=group_id)
        if GroupPage.is_member(creator, group):
            data = {'title': title,
                    'text': text,
                    'creator': creator.pk,
                    'group': group.pk}
            form = PostForm(data)
            if form.is_valid():
                post = form.instance
                if publish is None:
                    post.date_created = timezone.now()
                post.save()
                if group.is_private == True:
                    post.is_private = True
                    post.save()
                return HttpResponseRedirect('/posts/')
        return render(request, 'posts/post_create.html', {'error': "You must join group to create posts"})

class PostUpdate(LoginRequiredMixin, TemplateView):

    @staticmethod
    def is_creator(user_id, post_id):
        user = User.objects.get(pk=user_id)
        post = Post.objects.get(pk=post_id)
        creator = post.creator
        if creator.pk == user.pk:
            return True
        return False

    def get(self, request, post_id):
        user_id = request.user.pk
        template_name = 'posts/post_form.html'
        post = get_object_or_404(Post, pk=post_id)
        form = PostForm(instance=post)
        if self.is_creator(user_id, post_id):
            return render(request, template_name, {'form': form})
        else:
            return render(request, template_name, {'form': form, 'error':"Only creator is allowed to update the group" })


    def post(self, request, post_id):
        user_id = request.user.pk
        if self.is_creator(user_id, post_id):
            title = request.POST.get('title')
            text = request.POST.get('text')
            post = get_object_or_404(Post, pk=post_id)
            data = {'title': title, 'text': text, 'creator': post.creator.pk,
                    'group': post.group.pk}
            form = PostForm(data=data, instance=post)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(f'/posts/{post_id}')
        return render(request, 'posts/post_form.html', {'error': "Only creator is allowed to update the group"})

class PostDelete(LoginRequiredMixin, TemplateView):

    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        try:
            post.delete()
            return HttpResponseRedirect('/posts/')
        except:
            return HttpResponse("Couldn't delete", status=400)


class DraftsList(LoginRequiredMixin, ListView):

    def get(self, request):
        user = request.user
        posts = Post.objects.filter(creator=user, date_created=None).values()
        drafts = [elem for elem in posts]
        template_name = 'posts/drafts_list.html'
        return render(request, template_name, {'drafts': drafts})


@login_required
def publish(request, draft_id):
    if request.method == "POST":
        post = Post.objects.get(pk=draft_id)
        post.date_created = timezone.now()
        post.save()
        return HttpResponseRedirect('/drafts/')









