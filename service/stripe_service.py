import os 
import stripe
from datetime import time

class StripeService:
    def __init__(self):
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

    async def handle_stripe_customer(self, user):
        user_id = getattr(user, "id", "")
        customer_id = getattr(getattr(user, "subscription", None), "stripeCustomerId", None)
        if customer_id:
            try:
                stripe.Customer.retrieve(customer_id)
                return customer_id
            except Exception:
                customer_id = None 
        stripe_customer = stripe.Customer.create(
            email=getattr(user, "email", ""),
            name=getattr(user, "name", ""),
            metadata={
                "user_id": user_id
            }
        )
        customer_id = stripe_customer.id 

        if hasattr(user, "subscription"):
            user.subscription.stripeCustomerId = customer_id

        return customer_id

    async def add_usage_based_billing_info(self, user):

        payment_info = await self.check_customer_payment_method(user)
        if not payment_info["has_payment_method"]:
            return {
                "success": False,
                "error": "No payment method found. Please add a card first."
            }

        try:
            customer_id = await self.handle_stripe_customer(user)
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{
                    "price": os.getenv("STRIPE_PRICE_ID")
                }],
                expand=["latest_invoice.payment_intent"]
            )

            if hasattr(user, "subscription"):
                user.subscription.stripeSubscriptionId = subscription.id 
                user.subscription.stripeSubscriptionItemId = subscription["items"]["data"][0].id 

            return {
                "success": True,
                "subscription": subscription
            }
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def add_credit_for_usage_based(self, user, quantity):
        if not hasattr(user, "subscription") or not user.subscription.stripeSubscriptionItemId:
            return {
                "success": False,
                "error": "No active subscription found. Please subscribe first."
            }
            
        try:
            customer_id = await self.handle_stripe_customer(user)
            # Send a meter event instead of creating a usage record
            meter_event = stripe.billing.MeterEvent.create(
                event_name="api.request",  
                payload={
                    "stripe_customer_id": customer_id,
                    "value": quantity
                }
            )
            
            return {
                "success": True,
                "meter_event": {
                    "event_name": meter_event.event_name,
                    "timestamp": meter_event.timestamp if hasattr(meter_event, "timestamp") else None,
                    "status": meter_event.status if hasattr(meter_event, "status") else None,
                    "created": meter_event.created if hasattr(meter_event, "created") else None
                }
            }
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def create_setup_intent(self, user):
        customer_id = await self.handle_stripe_customer(user)
        setup_intent = stripe.SetupIntent.create(
            customer=customer_id,
            payment_method_types=['card'],
            usage='off_session' 
        )
        return setup_intent.client_secret

    async def create_customer_portal_session(self, user):
        customer_id = await self.handle_stripe_customer(user)
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
        )
        return session.url

    async def check_customer_payment_method(self, user):
        customer_id = await self.handle_stripe_customer(user)
        payment_methods = stripe.PaymentMethod.list(
            customer=customer_id,
            type="card"
        )
        
        if payment_methods and payment_methods.data:
            return {
                "has_payment_method": True,
                "cards": [{
                    "last4": card.card.last4,
                    "brand": card.card.brand,
                    "exp_month": card.card.exp_month,
                    "exp_year": card.card.exp_year
                } for card in payment_methods.data]
            }
        
        return {
            "has_payment_method": False,
            "cards": []
        }

    async def create_checkout_session(self, user, price, credits):
        try:
            user_id = user.id 
            customer_id = await self.handle_stripe_customer(user)
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {   
                            "name": f"{credits} Credits",
                            "description": f"{credits} processing minutes for audio separation"
                        },
                        "unit_amount": int(price * 100),
                    },
                    "quantity": 1,
                }],
                success_url=f"http://localhost:8000/verify-payment/id={{CHECKOUT_SESSION_ID}}",
                allow_promotion_codes=True,
                mode="payment",
                metadata={
                    "userId": user_id,
                    "credit": credits,
                    "price": price
                }
            )
            return {
                "url": session.url
            }
        except Exception as e:
            return {
                "error": str(e)
            }

    async def verify_payment(self, user, session_id):
        session = stripe.checkout.Session.retrieve(session_id)
        credits_to_add = float(session.metadata.get("credit", 0))
        price = float(session.metadata.get("price", 0))
        if session.payment_status == "paid":
            return {
                "success": True,
                "credit": credits_to_add,
                "price": price,
                "message": "Payment successful"
            }
        return {
            "success": False,
            "message": "Payment failed"
        }
    

