# Generated by Django 3.2.10 on 2024-05-31 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pong', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.ImageField(default='avatars/defaultAvatar.png', upload_to='avatars/'),
        ),
    ]
