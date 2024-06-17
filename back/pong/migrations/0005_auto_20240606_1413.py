# Generated by Django 3.2.10 on 2024-06-06 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pong', '0004_delete_imagemodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tournoi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tourn_name', models.CharField(blank=True, max_length=30)),
                ('tourn_winner', models.CharField(blank=True, max_length=30)),
                ('nb_players', models.IntegerField(default=0)),
                ('nb_rounds', models.IntegerField(default=0)),
            ],
        ),
        migrations.DeleteModel(
            name='Tournament',
        ),
    ]
