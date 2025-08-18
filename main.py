import os
from fastapi import FastAPI
from datetime import datetime, date, timedelta, timezone
from dotenv import load_dotenv
from user_model import User, create_dummy_user
from service.stripe_service import StripeService

load_dotenv()

app = FastAPI()
stripe_service = StripeService()

user = create_dummy_user()

def different_in_days(date1: date, date2: date) -> int:
    delta: timedelta = (date1 - date2)
    return delta.days

def previous_day() -> date:
    return (datetime.now() - timedelta(days=1)).date()

@app.get("/")
async def root() -> dict:
    return {
        "message": "it's working",
        "time": different_in_days(datetime.now(), datetime(2024, 2, 2, 2, 2, 2)),
        "previous_day": previous_day().isoformat(),
        "utc_time": datetime.now(timezone.utc)
    }

@app.post("/create-portal-session")
async def create_portal_session():
    
    portal_url = await stripe_service.create_customer_portal_session(user)
    
    return {"portal_url": portal_url}

@app.get("/check-card")
async def check_card():
    res = await stripe_service.check_customer_payment_method(user)
    return res

@app.post("/add-credit")
async def add_credit(credit: int):
    res = await stripe_service.add_credit_for_usage_based(user, credit)
    return res

@app.get("/create-checkout-session")
async def create_checkout_session():
    res = await stripe_service.create_checkout_session(user, 10, 100)
    return res

@app.post("/verify-payment")
async def verify_payment(session_id: str):
    res = await stripe_service.verify_payment(user, session_id)
    return res

@app.get("/add-user-info")
async def add_usage_based_billing_info():
    res = await stripe_service.add_usage_based_billing_info(user)
    return res

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "localhost"),
        port=int(os.getenv("PORT", 8001)),
        reload=True            
    )
