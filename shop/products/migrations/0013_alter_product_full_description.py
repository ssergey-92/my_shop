# Generated by Django 5.1 on 2024-10-07 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "products",
            "0012_rename_is_sale_product_is_sales_product_sales_from_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="full_description",
            field=models.CharField(default="See short description", max_length=5000),
        ),
    ]
