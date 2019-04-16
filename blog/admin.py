from django.contrib import admin
from .models import Group, Post, Membership

admin.site.register(Group)
admin.site.register(Post)
admin.site.register(Membership)