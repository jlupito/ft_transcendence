# Generated by Django 3.2.10 on 2024-05-10 16:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='elo',
        ),
    ]
