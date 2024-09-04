# Generated by Django 5.1 on 2024-08-24 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0002_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='unique_email',
            field=models.EmailField(max_length=254, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='unique_phone',
            field=models.CharField(max_length=12, null=True, unique=True),
        ),
    ]
