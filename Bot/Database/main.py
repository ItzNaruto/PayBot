from Bot import DATABASE
from bson import ObjectId

bots_collection = DATABASE.BOTS

async def get_bot_details(bot_id=None):
    if bot_id:
        return await bots_collection.find_one({"_id": ObjectId(bot_id)})
    return await bots_collection.find().to_list(length=10)

async def update_bot_price(bot_name, plan_name, new_price):
    return await bots_collection.update_one({"bot_name": bot_name}, {"$set": {f"plans.{plan_name}.price": new_price}})

async def create_new_bot(bot_name):
    bot_data = {
        "bot_name": bot_name,
        "plans": {
            "Silver": {"price": 50, "validity": "7 Days"},
            "Gold": {"price": 300, "validity": "1 Month"},
            "Platinum": {"price": 500, "validity": "6 Months"},
            "Diamond": {"price": 1000, "validity": "1 Year"},
        }
    }
    return await bots_collection.insert_one(bot_data)
