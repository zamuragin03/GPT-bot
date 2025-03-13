from .API import PaymentAPI
from Config import PAYMENT_SHOP_ID, PAYMENT_KEY, GROUP_LINK_URL
from yookassa import Configuration, Payment
import asyncio
import random


class PaymentService:
    def __init__(self, price, user_external_id, is_test=True):
        Configuration.account_id = PAYMENT_SHOP_ID
        Configuration.secret_key = PAYMENT_KEY
        self.price = price
        self.user_external_id = user_external_id,
        self.order_id = random.randint(10000, 999999)
        self.description = f'Order #{self.order_id}'

    def create_payment(self):
        PaymentAPI.CreatePayment(
            external_id=self.user_external_id,
            order_id=self.order_id,
            amount=self.price)
        payment = Payment.create({
            "amount": {
                "value": self.price,
                "currency": "RUB"
            },
            "payment_method_data": {
                "type": "bank_card"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": GROUP_LINK_URL
            },
            "metadata": {
                'orderNumber': self.order_id
            },
            "description": self.description,
            "capture": True,

        })
        self.order_detail = payment
        return self.order_detail

    async def check_payment(self,):
        payment_id = self.order_detail.id
        while self.order_detail['status'] == 'pending':
            self.order_detail = Payment.find_one(payment_id)
            await asyncio.sleep(3)

        if self.order_detail['status'] == 'succeeded':
            PaymentAPI.UpdatePayment(
                order_id=self.order_id,
                status='success'
            )
            return True
        else:
            PaymentAPI.UpdatePayment(
                order_id=self.order_id,
                status='fail'
            )
            return False
