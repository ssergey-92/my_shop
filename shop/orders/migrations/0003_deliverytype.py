# Generated by Django 5.1 on 2024-09-18 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0002_orderandproduct_order_products"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeliveryType",
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
                ("name", models.CharField(max_length=100, unique=True)),
            ],
            options={
                "verbose_name": "Order: delivery type",
                "verbose_name_plural": "Order: delivery types",
            },
        ),
    ]
