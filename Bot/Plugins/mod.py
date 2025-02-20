from Bot import app, MODS_ID
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from Bot.Database import create_new_bot, get_bot_details, update_bot_price

@app.on_message(filters.command("newbot") & filters.user(MODS_ID))
async def new_bot(client, message):
    bot_name = message.text.split(" ", 1)[1]
    await create_new_bot(bot_name)
    await message.reply(f"New bot '{bot_name}' created successfully!")

@app.on_message(filters.command("setprice") & filters.user(MODS_ID))
async def set_price(client, message):
    args = message.text.split(" ")
    bot_name, plan_name, price = args[1], args[2], int(args[3])
    await update_bot_price(bot_name, plan_name, price)
    await message.reply(f"Price for {plan_name} plan in bot {bot_name} updated to {price} Rs.")

@app.on_message(filters.command("showplans") & filters.user(MODS_ID))
async def show_plans(client, message):
    bot_name = message.text.split(" ", 1)[1]
    bot_details = await get_bot_details(bot_name)
    
    if bot_details:
        plans = bot_details["plans"]
        plan_text = "\n".join([f"{plan}: Price = {details['price']} Rs, Validity = {details['validity']}" for plan, details in plans.items()])
        await message.reply(f"Plans for {bot_name}:\n{plan_text}")
    else:
        await message.reply("Bot not found!")
