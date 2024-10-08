# Generated by Django 5.1 on 2024-09-14 17:02

import products.models.category_image
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CategoryImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "src",
                    models.ImageField(
                        max_length=150,
                        upload_to=products.models.category_image.get_category_image_saving_path,
                    ),
                ),
                (
                    "alt",
                    models.CharField(
                        default="Image is currently unavailable!", max_length=150
                    ),
                ),
            ],
            options={
                "verbose_name": "Category: image",
                "verbose_name_plural": "Categories: images",
            },
        ),
    ]
