"""Module with app services."""

import json
from random import choice as rdm_choice
from traceback import print_exception as tb_print_exception
from typing import Optional


from cryptography.fernet import Fernet, InvalidToken
from os import getenv as os_getenv

from pydantic import ValidationError

from app_logger import app_logger
from schema import PaymentDetails

class PaymentHandler:
    _fernet = Fernet(bytes(os_getenv("PAYMENT_KEY"), os_getenv("ENCODING")))
    _server_error = "Internal Server Error!"
    _payment_data_error = "Invalid payments details"
    _security_error = "Payment denied due to security reason!"
    _payment_errors = [
        "Not enough money on the card!",
        "Invalid card details!",
        "Card is expired!",
        "Card is blocked!",
    ]
    _successful_payment_msg = "Successfully payment transaction."

    @classmethod
    def conduct_user_payment(cls, request_body: bytes) -> tuple[bytes, int]:
        """Handle logic to charge payment from user's card.

        Decrypt and validate payments details and charge payment.
        Return corresponding response.

        """
        response_data = (cls._server_error, 500)
        try:
            payment_details = cls._get_payment_details(request_body)
            payment_error = cls._charge_user(payment_details)
            if payment_error:
                response_data = (payment_error, 400)
            else:
                response_data = (cls._successful_payment_msg, 200)
        except ValidationError as exc:
            app_logger.info(tb_print_exception(exc))
            response_data = [cls._payment_data_error , 400]
        except InvalidToken as exc:
            app_logger.error(tb_print_exception(exc))
            response_data = (cls._security_error, 400)
        except Exception as exc:
            app_logger.error(tb_print_exception(exc))
        finally:
            encrypted_msg = cls._get_encrypted_msg({"msg": response_data[0]})
            app_logger.info(
                f"Bank response: {encrypted_msg=} | {response_data[1]}"
            )
            return encrypted_msg, response_data[1]

    @classmethod
    def _get_payment_details(cls, request_body: bytes) -> PaymentDetails:
        """Decrypt and validate payment details from request body."""

        app_logger.debug(f"Request body: {request_body}")
        decrypted_data = cls._fernet.decrypt(request_body)
        data = json.loads(decrypted_data)
        app_logger.debug(f"Payment data: {data}")
        return PaymentDetails(**data)

    @classmethod
    def _charge_user(cls, payment_details: PaymentDetails) -> Optional[str]:
        """Charge payment from user.

        If cardholder number is divisible by two without reminder and does not
        end with zero then payment considered successful and return None.
        Else return random error msg.

        """
        app_logger.debug(f"Card number: {payment_details.number}")
        card_number = int(payment_details.number)
        if (card_number % 10 != 0) and (card_number % 2 == 0):
            app_logger.debug(f"Success payment for card: {card_number}")
            return

        random_error_msg = rdm_choice(cls._payment_errors)
        app_logger.debug(f"Random payment error msg: {random_error_msg}")
        return random_error_msg

    @classmethod
    def _get_encrypted_msg(cls, msg: dict) -> bytes:
        """Encrypt msg by Fernet."""

        app_logger.debug(f"Msg to encrypt: {msg}")
        msg = json.dumps(msg).encode(os_getenv("ENCODING"))
        return cls._fernet.encrypt(msg)
