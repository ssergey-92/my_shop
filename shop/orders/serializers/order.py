from datetime import datetime
from decimal import Decimal
from typing import Optional

from rest_framework import serializers

from common.validators import validate_full_name, validate_phone_number
from orders.models import Order, PaymentType, DeliveryType
from orders.validators import validate_address, validate_city_name
from products.serializers import OutSpecialProductSerializer


allowed_payment_types = PaymentType.objects.values_list('name', flat=True)
allowed_delivery_types = DeliveryType.objects.values_list('name', flat=True)
payment_type_error = (
    "Payment: {payment_type} is denied! "
    "\nAllowed types: {allowed_payment_types}"
)
delivery_type_error = (
    "Delivery type: {delivery_type} is not supported! "
    "\nAllowed types: {allowed_delivery_types}"
)


class OrderConfirmationSerializer(serializers.Serializer):
    """Class is used for validation and sorting order confirmation data.

    Order confirmation data is taken from request body of POST /order/{id} .

    """
    fullName = serializers.CharField()
    email = serializers.EmailField(required=True)
    phone = serializers.CharField()
    paymentType = serializers.CharField(
        required=False, allow_blank=True, allow_null=True,
    )
    city = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    deliveryType = serializers.CharField(
        required=False, allow_blank=True, allow_null=True,
    )

    def validate_phone(self, phone: Optional[str]) -> Optional[str]:
        """Extra validation for 'phone' field."""

        if phone is None:
            return

        phone = phone.strip()
        validation_error = validate_phone_number(phone)
        if not validation_error:
            return phone

        raise serializers.ValidationError(validation_error)

    def validate_fullName(self, full_name: Optional[str]) -> Optional[str]:
        """Extra validation for 'fullName' field."""

        if full_name is None:
            return

        full_name = full_name.strip()
        validation_error = validate_full_name(full_name)
        if not validation_error:
            return full_name

        raise serializers.ValidationError(validation_error)

    def validate_paymentType(self, payment_type: str) -> Optional[str]:
        """Extra validation for 'paymentType' field."""

        if not payment_type or (payment_type in allowed_payment_types):
            return payment_type

        raise serializers.ValidationError(
            payment_type_error.format(
                payment_type=payment_type,
                allowed_payment_types=allowed_payment_types,
            ),
        )

    def validate_city(self, city: str) -> str:
        """Extra validation for 'city' field."""

        city = city.strip()
        validation_error = validate_city_name(city)
        if not validation_error:
            return city

        raise serializers.ValidationError(validation_error)

    def validate_address(self, address: str) -> str:
        """Extra validation for 'address' field."""

        address = address.strip()
        validation_error = validate_address(address)
        if not validation_error:
            return address

        raise serializers.ValidationError(validation_error)

    def validate_deliveryType(
            self, delivery_type: Optional[str],
    ) -> Optional[str]:
        """Extra validation for 'deliveryType' field."""

        if not delivery_type or (delivery_type in allowed_delivery_types):
            return delivery_type

        raise serializers.ValidationError(
            delivery_type_error.format(
                delivery_type=delivery_type,
                allowed_delivery_types=allowed_delivery_types,
            ),
        )

    def to_representation(self, instance: dict) -> dict:
        """Sort validated data to required user format."""

        return {
            "fullname": instance.get("fullName", None),
            "email": instance.get("email", None),
            "phone": instance.get("phone", None),
            "payment_type": instance.get("paymentType", None),
            "city": instance.get("city", None),
            "address": instance.get("address", None),
            "delivery_type": instance.get("deliveryType", None),
        }


class OrderedProductSerializer(serializers.Serializer):
    """Class is used for validation and sorting ordered product data.

    Product data is taken from request body of POST /order (create order).

    """
    id = serializers.IntegerField(min_value=1, required=True)
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=True,
    )
    count = serializers.IntegerField(min_value=1, required=True)

    def validate_price(self, value: Decimal):
        """Extra validation for 'price' field."""

        if float(value) > 0:
            return value

        raise serializers.ValidationError("Price should be grater then 0!")

    def to_representation(self, instance: dict) -> dict:
        """Sort validated data to required user format."""

        return {
            "product_id": instance["id"],
            "total_price": instance["price"]  * instance["count"],
            "total_quantity": instance["count"],
        }


class OutOrderSerializer(serializers.ModelSerializer):
    """Class is used for serializing order."""

    createdAt = serializers.SerializerMethodField()
    fullName = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    deliveryType = serializers.SerializerMethodField()
    paymentType = serializers.SerializerMethodField()
    totalCost = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "id",
            "createdAt",
            "fullName",
            "email",
            "phone",
            "deliveryType",
            "paymentType",
            "totalCost",
            "status",
            "city",
            "address",
            "products",
        )

    def get_createdAt(self, obj: Order) -> datetime:
        """Get order created time."""

        return obj.created_at.strftime('%d %b %Y %H:%M')

    def get_fullName(self, obj: Order) -> Optional[str]:
        """Get receiver full name."""

        return (
            obj.receiver_fullname or obj.created_by.profile.full_name or None
        )

    def get_email(self, obj: Order) -> Optional[str]:
        """Get receiver email."""

        return (
            obj.receiver_email or obj.created_by.profile.unique_email or None
        )

    def get_phone(self, obj: Order) -> Optional[str]:
        """Get receiver phone number."""

        return (
            obj.receiver_phone or obj.created_by.profile.unique_phone or None
        )

    def get_deliveryType(self, obj: Order) -> str:
        """Get order delivery type name."""

        return obj.delivery_type.name if obj.delivery_type else None

    def get_paymentType(self, obj: Order) -> Optional[str]:
        """Get order payment type name."""

        return obj.payment_type.name if obj.payment_type else  None

    def get_totalCost(self, obj: Order) -> Decimal:
        """Get total cost of order."""

        return obj.total_cost

    def get_status(self, obj: Order) -> Optional[str]:
        """Get order status name with payment comment if existed."""
        if obj.status:
            if obj.payment_comment:
                return obj.status.name + " (" + obj.payment_comment + ")"

            return obj.status.name
        return None

    def get_products(self, obj: Order) -> list:
        """Get ordered product."""

        products = obj.products.filter(is_active=True).all()
        products_data = []
        if not products:
            return products_data
        for i_product in products:
            i_product_data = OutSpecialProductSerializer(i_product).data
            # Override with product purchased total quantity
            ordered_product = (
                obj.orderandproduct_set.filter(product=i_product).first()
            )
            i_product_data["count"] = ordered_product.total_quantity
            products_data.append(i_product_data)

        return products_data
