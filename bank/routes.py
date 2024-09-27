"""Module with bank routes."""

from flask import Flask, request

from services import PaymentHandler

app = Flask("my_bank")


@app.route('/users/payment', methods=['POST'])
def charge_user() -> tuple[bytes, int]:
    """Charge payment form user's card."""

    return PaymentHandler.conduct_user_payment(request.data)
