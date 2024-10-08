# Generated by Django 5.1 on 2024-08-24 14:45

import django.db.models.deletion
import user_profile.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Avatar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('src', models.ImageField(max_length=150, upload_to=user_profile.models.get_avatar_path)),
                ('alt', models.CharField(default='Your profile photo is currently unavailable.', max_length=150)),
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='user_profile.profile')),
            ],
        ),
    ]
