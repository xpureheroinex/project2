from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (ListView, DetailView, TemplateView)
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from .models import Group
from .forms import GroupForm


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
                return HttpResponse(settings.LOGIN_ERROR_MESSAGE, status=401)
        except User.DoesNotExist:
            return HttpResponse(settings.LOGIN_ERROR_MESSAGE, status=401)

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


class GroupsList(ListView):

    model = Group
    template_name = 'groups/groups_list.html'


class GroupInfo(DetailView):

    model = Group
    template_name = 'groups/group_info.html'


class GroupCreate(TemplateView):

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


class GroupUpdate(TemplateView):

    def get(self, request):
        template_name = "groups/group_form.html"
        return render(request, template_name=template_name)

    def post(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id)
        name = request.POST.get('name')
        theme = request.POST.get('theme')
        data = {'name': name, 'theme': theme, 'creator': group.pk}
        form = GroupForm(data=data, instance=group)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(f'/groups/{group_id}/')
        return HttpResponse("Update wasn't successful", status=400)








