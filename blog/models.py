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
    members = models.ManyToManyField(User, through='Membership', related_name='members', null=True)

    def __str__(self):
        return self.name

    @classmethod
    def create(cls, name, theme, creator):
        group = Group(name=name, theme=theme, creator=creator)
        return group


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date_joined = models.DateTimeField()


    def __str__(self):
        return f"{self.user.username} in {self.group.name} group"