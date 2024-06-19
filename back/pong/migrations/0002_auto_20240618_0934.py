# Generated by Django 3.2.10 on 2024-06-18 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pong', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='elo',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='matches_lost',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='matches_won',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='tourn_won',
            field=models.IntegerField(default=0),
        ),
    ]