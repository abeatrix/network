# Generated by Django 3.1.7 on 2021-04-12 23:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0003_delete_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='username',
        ),
    ]