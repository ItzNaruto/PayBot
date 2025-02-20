from Bot import DATABASE

user_db = DATABASE["USERS"]

async def is_served_user(user_id: int) -> bool:
    user = await user_db.find_one({"user_id": user_id})
    return user is not None

async def add_user_to_db(user_id: int):
    if not await is_served_user(user_id):
        await user_db.insert_one({"user_id": user_id})

async def get_users_list():
    users = user_db.find({"user_id": {"$gt": 0}})
    return [user["user_id"] async for user in users]
