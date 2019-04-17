from .models import Group, Post
from django import forms
from django.contrib.auth.models import User

class GroupForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = ['name', 'theme', 'creator']

    name = forms.CharField(label='name', max_length=100)
    theme = forms.ChoiceField(choices=Group.THEME_CHOICES)

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'text', 'creator', 'group']

    title = forms.CharField(label='title', max_length=100)
    text = forms.Textarea()
