# Generated by Django 3.2.10 on 2024-06-18 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pong', '0002_auto_20240618_0934'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='player1_notUser',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='match',
            name='player2_notUser',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]