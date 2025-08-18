from dataclasses import dataclass
from typing import Optional

@dataclass
class Subscription:
    stripeCustomerId: Optional[str] = None
    stripeSubscriptionId: Optional[str] = None
    stripeSubscriptionItemId: Optional[str] = None

@dataclass
class User:
    id: str
    name: str
    email: str
    subscription: Optional[Subscription] = None

def create_dummy_user() -> User:
    return User(
        id="user_123",
        name="Test User",
        email="test@example.com",
        subscription=Subscription()
    )
    