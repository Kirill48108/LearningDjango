import stripe
from django.conf import settings


class StripeService:
    def __init__(self):
        if not settings.STRIPE_API_KEY:
            raise RuntimeError("STRIPE_API_KEY is not configured")
        stripe.api_key = settings.STRIPE_API_KEY
        self.currency = getattr(settings, "STRIPE_CURRENCY", "rub")
        self.success_url = getattr(settings, "STRIPE_SUCCESS_URL", "http://localhost:8000/success")
        self.cancel_url = getattr(settings, "STRIPE_CANCEL_URL", "http://localhost:8000/cancel")

    def create_product(self, name: str) -> dict:
        product = stripe.Product.create(name=name)
        return product

    def create_price(self, product_id: str, amount) -> dict:
        # Stripe принимает цену в минимальных единицах (копейках): умножаем на 100
        unit_amount = int(round(float(amount) * 100))
        price = stripe.Price.create(
            unit_amount=unit_amount,
            currency=self.currency,
            product=product_id,
        )
        return price

    def create_checkout_session(self, price_id: str) -> dict:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=self.success_url,
            cancel_url=self.cancel_url,
        )
        return session

    def retrieve_session(self, session_id: str) -> dict:
        session = stripe.checkout.Session.retrieve(session_id)
        return session
