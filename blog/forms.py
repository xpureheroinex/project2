from .models import Group
from django import forms
from django.contrib.auth.models import User

class GroupForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = ['name', 'theme']

    name = forms.CharField(label='name', max_length=100)
    theme = forms.ChoiceField(choices=Group.THEME_CHOICES)
