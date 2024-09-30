import traceback
from typing import Optional

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db import transaction
from django.db.models import QuerySet

from rest_framework.exceptions import ValidationError

from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from .common import DeliveryService
from common.custom_logger import app_logger
from common.utils import server_error
from orders.exceptions import OrderException
from orders.models import (
    DeliveryType,
    Order,
    OrderAndProduct,
    OrderStatus,
    Product,
    PaymentType,
)
from orders.serializers import (
    OrderConfirmationSerializer,
    OrderedProductSerializer,
    OutOrderSerializer,
)

empty_order_error = {"error": "Order should include at least 1 Product!"}
unavailable_products_error = "Following products are not available: {products}"
purchased_qnty_error  = (
    "There are {available_qnty} '{title}' available instead of "
    "{purchased_qnty}!"
)
unexsist_order_error = "Order with {id} is not exist!"


class OrderHandler:
    """Class for handling business logic of product order related endpoints."""

    _created_order_status = OrderStatus.objects.get(name="created")
    _confirmed_order_status = OrderStatus.objects.get(name="confirmed")
    _ordinary_delivery_type = DeliveryType.objects.get(name="ordinary")
    _express_delivery_type = DeliveryType.objects.get(name="express")
    _online_payment_type = PaymentType.objects.get(name="online")
    _someone_payment_type = PaymentType.objects.get(name="someone")

    @classmethod
    def get_order_by_id(cls, order_id: int) -> Response:
        """Handle logic to get active order by id."""

        try:
            order = Order.get_by_id_with_prefetch(order_id)
            order_data = OutOrderSerializer(order).data
            return Response(order_data, HTTP_200_OK)
        except Order.DoesNotExist:
            return Response(
                unexsist_order_error.format(id=order_id), HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:
            app_logger.error(traceback.print_exception(exc))
            return Response(server_error, HTTP_500_INTERNAL_SERVER_ERROR)

    @classmethod
    def get_user_orders(cls, user: User) -> Response:
        """Handle logic to get user's active orders."""

        try:
            orders = (
                Order.get_user_orders_with_prefetch(user).
                order_by("-created_at")
            )
            orders_data = OutOrderSerializer(orders, many=True).data
            return Response(orders_data, HTTP_200_OK)
        except Exception as exc:
            app_logger.error(traceback.print_exception(exc))
            return Response(server_error, HTTP_500_INTERNAL_SERVER_ERROR)

    @classmethod
    def create_init_order(
            cls, order_details: dict, user: User, session: Session
    ) -> Response:
        """Handle logic for creating 'init' order.

        If request body is valid then check and reduce stock products quantity
        (lock ordered products in db while updating them), create order with
        status "Created" and clean basket.  Return corresponding response.

        """

        try:
            order_data = cls._get_init_order_data(order_details)
            products_ids = list(order_data["products"].keys())
            with transaction.atomic():
                stock_products = Product.select_available_products(
                    products_ids
                )
                if len(order_data["products"]) != stock_products.count():
                    cls._raise_unavailable_products_error(products_ids)

                order = Order.objects.create(
                    created_by=user,
                    products_cost=order_data["cost"],
                    total_cost=order_data["cost"],
                    status=cls._created_order_status,
                )
                cls._reduce_stock_products(
                    stock_products, order_data["products"]
                )
                OrderAndProduct.bulk_add(
                    order_data["products"].values(), order.id
                )
            session.pop("basket", None)
            return Response({"orderId": order.id}, HTTP_200_OK)
        except ValidationError as exc:
            return Response({"error": str(exc)}, HTTP_400_BAD_REQUEST)
        except Exception as exc:
            app_logger.error(traceback.print_exception(exc))
            return Response(server_error, HTTP_500_INTERNAL_SERVER_ERROR)

    @classmethod
    def confirm_order(cls, order_details:dict, order_id: int) -> Response:
        """Handle logic for confirming order.

        If request body data is valid then update init order(order_id).
        Return corresponding response.

        """
        try:
            order_data = OrderConfirmationSerializer(data=order_details)
            order_data.is_valid(raise_exception=True)
            with transaction.atomic():
                order = Order.objects.select_for_update().get(id=order_id)
                cls._update_init_order(order, order_data.data)
            return Response({"orderId": order.id}, status=HTTP_200_OK)
        except (ValidationError, Order.DoesNotExist) as exc:
            return Response({"error": str(exc)}, HTTP_400_BAD_REQUEST)
        except Exception as exc:
            app_logger.error(traceback.print_exception(exc))
            return Response(server_error, HTTP_500_INTERNAL_SERVER_ERROR)

    @classmethod
    def _get_delivery_type(cls, delivery_name: Optional[str]) -> DeliveryType:
        """Get delivery type as per delivery name.

        If delivery name is None then use default delivery type 'ordinary'.

        """
        if not delivery_name or delivery_name == "ordinary":
            return cls._ordinary_delivery_type

        return cls._express_delivery_type

    @classmethod
    def _get_payment_type(cls, payment_name: Optional[str]) -> PaymentType:
        """Get payment type as per payment name.

        If payment name is None then use default payment type 'online'.

        """
        if not payment_name or payment_name == "online":
            return cls._online_payment_type

        return cls._someone_payment_type

    @classmethod
    def _update_init_order(
            cls, init_order: Order, confirm_order_data: dict,
    ) -> None:
        """Update init order(status=created) with data from 'confirm order'."""

        init_order.status = cls._confirmed_order_status
        init_order.receiver_fullname = confirm_order_data.get("fullname", None)
        init_order.receiver_phone = confirm_order_data.get("phone", None)
        init_order.receiver_email = confirm_order_data["email"]
        init_order.address = confirm_order_data["address"]
        init_order.city = confirm_order_data["city"]
        init_order.payment_type = cls._get_payment_type(
            confirm_order_data.get("payment_type", None)
        )
        init_order.delivery_type = cls._get_delivery_type(
            confirm_order_data.get("delivery_type", None)
        )
        init_order.delivery_cost = DeliveryService.count_cost(
            init_order.products_cost, init_order.delivery_type
        )
        init_order.total_cost = (
                init_order.delivery_cost + init_order.products_cost
        )
        init_order.save()

    @staticmethod
    def _get_init_order_data(request_data: dict) -> dict:
        """Validate and sort 'init order' data from request body."""

        products = {}
        order_cost = 0
        for i_product in request_data:
            product_data = OrderedProductSerializer(data=i_product)
            product_data.is_valid(raise_exception=True)
            order_cost += product_data.data["total_price"]
            products[product_data.data["product_id"]] = product_data.data

        return {"products": products, "cost": order_cost}


    @staticmethod
    def _raise_unavailable_products_error(products_ids: list[int]) -> None:
        """Raise error if product in order is not available in stock."""

        unavailable_products = Product.get_unavailable_products(products_ids)
        products_titles = unavailable_products.values_list("title", flat=True)
        raise OrderException(
            unavailable_products_error.format(products=products_titles)
        )

    @staticmethod
    def _reduce_stock_products(
            stock_products: QuerySet, ordered_products: dict,
    ) -> None:
        """Reduce stock products quantity according to ordered quantity."""

        for stock_product in stock_products:
            ordered_product = ordered_products[stock_product.id]
            if stock_product.count < ordered_product["total_quantity"]:
                raise OrderException(purchased_qnty_error.format(
                    available_qnty=stock_product.count,
                    title=stock_product.title,
                    purchased_qnty=ordered_product["total_quantity"],
                    )
                )

            stock_product.count -= ordered_product["total_quantity"]
            stock_product.save()
