from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from orders.models import Product
from products.serializers import OutSpecialProductSerializer


class BasketAddItemSerializer(serializers.Serializer):
    """Class is used for validation request body to add new item in bucket."""

    id = serializers.IntegerField(required=True, allow_null=False)
    count = serializers.IntegerField(required=True, allow_null=False)


    def validate(self, data) -> dict:
        """Extra product id and count validation.

        Check that product id is existed and active and remains products >=
        user purchased quantity.
        """

        product = Product.objects.get(id=data["id"], is_active=True)
        if not product:
            raise ValidationError(f"Product id: {data["id"]} is not existed!")
        elif product.count == 0:
            raise ValidationError(
                f"Product with id: {data["id"]} is not available!"
                f"\nRemains products = 0"
            )
        elif product.count < data["count"]:
            raise ValidationError(
                f"There are only {product.count} {product.title} available!"
                f"Reduce purchased quantity or select another product!"
            )
        return data


class BucketProductSerializer(OutSpecialProductSerializer):
    """Serializing db model 'Product' for basket."""

    count = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()


    class Meta(OutSpecialProductSerializer.Meta):  # Inherit Meta class
        fields = OutSpecialProductSerializer.Meta.fields

    def get_count(self, obj: Product) -> int:
        """Override model 'count' field.

        Set user required quantity 'count' instead of product available
        quantity 'count'.

        """
        if obj.required_amount <= obj.count:
            return obj.required_amount
        else:
            return obj.count


    def get_price(self, obj: Product) -> float:
        """Override model 'price' field.

        Set total 'price' instead of product 'price' according to the quantity.

        """
        count = self.get_count(obj)
        return float(count * obj.price)