from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Group(models.Model):

    THEME_CHOICES = (
        ('GE', 'General'),
        ('MU', 'Music'),
        ('SP', 'Sport'),
        ('TV', 'Television'),
        ('PL', 'Politics'),
        ('SP', 'Space'),
        ('HE', 'Health')
    )

    name = models.CharField(max_length=100)
    theme = models.CharField(choices=THEME_CHOICES, max_length=2)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='creator')
    date_created = models.DateTimeField(default=timezone.now)
    members = models.ManyToManyField(User, through='Membership', related_name='members')
    is_private = models.BooleanField(default=False)


    def __str__(self):
        return self.name

    @classmethod
    def create(cls, name, theme, creator):
        group = Group(name=name, theme=theme, creator=creator)
        group.save()
        return group


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date_joined = models.DateTimeField()

    @classmethod
    def create(cls, user, group):
        membership = Membership(user=user, group=group, date_joined=timezone.now)
        membership.save()
        return membership


    def __str__(self):
        return f"{self.user.username} in {self.group.name} group"


class Post(models.Model):

    title = models.CharField(max_length=100)
    text = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_creator')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='post_group')
    date_created = models.DateTimeField(null=True)
    is_private = models.BooleanField(default=False)

    @classmethod
    def create(cls, title, text, creator, group):
        post = Post(title=title, text=text, creator=creator,
                    group=group)
        post.save()
        return post

