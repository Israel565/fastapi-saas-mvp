import stripe

from .config import settings

stripe.api_key = settings.stripe_secret_key

PRICE_ID = "price_xxx"  # create in Stripe dashboard


def create_checkout_session(customer_email: str) -> str:
    """Create a Stripe Checkout Session for subscription."""
    session = stripe.checkout.Session.create(
        mode="subscription",
        customer_email=customer_email,
        line_items=[{"price": PRICE_ID, "quantity": 1}],
        success_url=f"{settings.frontend_url}/?success=1",
        cancel_url=f"{settings.frontend_url}/?cancel=1",
    )
    return session.url


def verify_webhook(payload: bytes, sig_header: str) -> dict:
    """Verify and parse Stripe webhook event."""
    event = stripe.Webhook.construct_event(
        payload, sig_header, "whsec_xxx"  # set your webhook secret
    )
    return event
