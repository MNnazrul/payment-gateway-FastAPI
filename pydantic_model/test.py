from pydantic import BaseModel, Field
import motor.motor_asyncio
import asyncio


class User(BaseModel):
    username: str = Field(..., description="Unique username for the user")
    age: int = Field(default=18, description="User age, defaults to 18")


client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["new_database_test"]
user_collection = db["user"]

async def create_user(user: User):
    try:
        result = await user_collection.insert_one(user.model_dump())
        print(f"Inserted user with id: {result.inserted_id}")
    except Exception as e:
        print(f"Error inserting user: {e}")

async def main():
    await user_collection.create_index("username", unique=True)

    user1 = User(username="alice")
    user2 = User(username="alice")

    await create_user(user1)
    await create_user(user2)


if __name__ == "__main__":
    asyncio.run(main())
