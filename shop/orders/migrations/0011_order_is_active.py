# Generated by Django 5.1 on 2024-09-22 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0010_deliverytype_free_delivery_order_price_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]
