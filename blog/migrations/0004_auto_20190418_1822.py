# Generated by Django 2.2 on 2019-04-18 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_post_is_private'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='is_private',
        ),
        migrations.AddField(
            model_name='group',
            name='is_private',
            field=models.BooleanField(default=False),
        ),
    ]
