from Bot import app, LOG_CHANNEL, QR_PIC_URL, UPI_ID, MODS_ID
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from Bot.Database import get_bot_details, add_user_to_db, get_users_list
from bson import ObjectId

@app.on_message(filters.command("start"))
async def start(client, message):
    if not message.from_user:
        return
        
    user_id = message.from_user.id
    
    try:
        if user_id not in await get_users_list():
            await add_user_to_db(user_id)
    except Exception:
        pass

    bot_details = await get_bot_details()
    if not bot_details:
        return await message.reply("🚫 **No bots available for selection.**")

    keyboard = [
        [
            InlineKeyboardButton(f"🤖 {bot_details[i]['bot_name']}", callback_data=f"sel_{str(bot_details[i]['_id'])}"),
            InlineKeyboardButton(f"🤖 {bot_details[i + 1]['bot_name']}", callback_data=f"sel_{str(bot_details[i + 1]['_id'])}")
        ]
        for i in range(0, len(bot_details) - 1, 2)
    ]
    if len(bot_details) % 2 != 0:
        keyboard.append([InlineKeyboardButton(f"🤖 {bot_details[-1]['bot_name']}", callback_data=f"sel_{str(bot_details[-1]['_id'])}")])

    await message.reply(
        text="✨ **Welcome to UPI Plan Bot!**\n\n"
             "💎 **Unlock Premium Plans for Exclusive Benefits!**\n"
             "📜 **Choose a bot from the list below:**",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@app.on_callback_query(filters.regex(r"^sel_"))
async def select_plan(client, callback_query):
    bot_id = callback_query.data.split("_")[1]
    bot_details = await get_bot_details(bot_id)
    if not bot_details:
        return await callback_query.answer("⚠️ **Bot not found!**", show_alert=True)

    plans = list(bot_details["plans"].keys())
    keyboard = [
        [
            InlineKeyboardButton(f"💎 {plans[i]}", callback_data=f"pln_{bot_id}_{plans[i]}"),
            InlineKeyboardButton(f"💎 {plans[i + 1]}", callback_data=f"pln_{bot_id}_{plans[i + 1]}")
        ]
        for i in range(0, len(plans) - 1, 2)
    ]
    if len(plans) % 2 != 0:
        keyboard.append([InlineKeyboardButton(f"💎 {plans[-1]}", callback_data=f"pln_{bot_id}_{plans[-1]}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="start")])

    await callback_query.message.delete()
    await callback_query.message.reply(
        text=f"📌 **{bot_details['bot_name']} - Select Your Premium Plan:**",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@app.on_callback_query(filters.regex(r"^pln_"))
async def plan_details(client, callback_query):
    _, bot_id, plan_name = callback_query.data.split("_")
    bot_details = await get_bot_details(bot_id)
    plan = bot_details["plans"].get(plan_name)
    
    if not plan:
        return await callback_query.answer("⚠️ **Plan not found!**", show_alert=True)

    keyboard = [
        [InlineKeyboardButton("🛒 Purchase Now", callback_data=f"buy_{bot_id}_{plan_name}")],
        [InlineKeyboardButton("🔙 Back", callback_data=f"sel_{bot_id}")]
    ]

    await callback_query.message.delete()
    await callback_query.message.reply(
        text=f"🌟 **{bot_details['bot_name']} - {plan_name} Plan**\n\n"
             "🚀 **Enjoy These Exclusive Benefits:**\n"
             "✅ **Direct File Access**\n"
             "🚫 **No Ads or Shorteners**\n"
             "⚡ **High-Speed Access**\n"
             "🎁 **And Much More!**\n\n"
             f"💰 **Price:** `{plan['price']} Rs`\n"
             f"⏳ **Validity:** `{plan['validity']}`",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@app.on_callback_query(filters.regex(r"^buy_"))
async def buy_plan(client, callback_query):
    _, bot_id, plan_name = callback_query.data.split("_")
    bot_details = await get_bot_details(bot_id)
    plan = bot_details["plans"].get(plan_name)

    keyboard = [
        [InlineKeyboardButton("✅ Confirm Purchase", callback_data=f"cnf_{bot_id}_{plan_name}")],
        [InlineKeyboardButton("❌ Cancel", callback_data=f"sel_{bot_id}")]
    ]

    await callback_query.message.delete()
    await callback_query.message.reply(
        text=f"🛍 **Confirm Your Purchase - {bot_details['bot_name']} {plan_name} Plan**\n\n"
             f"💰 **Price:** `{plan['price']} Rs`\n"
             f"⏳ **Validity:** `{plan['validity']}`\n\n"
             "🛒 **Click 'Confirm Purchase' to proceed with payment!**",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@app.on_callback_query(filters.regex(r"^cnf_"))
async def payment_details(client, callback_query):
    _, bot_id, plan_name = callback_query.data.split("_")
    bot_details = await get_bot_details(bot_id)
    plan = bot_details["plans"].get(plan_name)

    keyboard = [
        [InlineKeyboardButton("📸 Upload Payment Proof", callback_data=f"prf_{bot_id}_{plan_name}")],
        [InlineKeyboardButton("❌ Cancel", callback_data=f"sel_{bot_id}")]
    ]

    await callback_query.message.delete()
    await callback_query.message.reply_photo(
        QR_PIC_URL,
        caption=f"📌 **Payment Details for {bot_details['bot_name']} - {plan_name} Plan**\n\n"
                f"💳 **UPI ID:** `{UPI_ID}`\n\n"
                "📍 **After completing the payment, please upload a screenshot for verification.**",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@app.on_callback_query(filters.regex(r"^prf_"))
async def request_screenshot(client, callback_query):
    _, bot_id, plan_name = callback_query.data.split("_")
    bot_details = await get_bot_details(bot_id)

    await callback_query.message.delete()
    verification_msg = await callback_query.message.reply(
        text="📤 **Upload Your Payment Screenshot with Transaction ID Now!**\n\n"
             "⚠️ **Other screenshots will be rejected!**"
    )

    @app.on_message(filters.photo & filters.user(callback_query.from_user.id))
    async def verify_payment(client, message):
        user = message.from_user
        photo_id = message.photo.file_id

        sent_message = await app.send_photo(
            LOG_CHANNEL,
            photo_id,
            caption=f"🔔 **Payment Verification Request:**\n"
                    f"👤 **User:** [{user.first_name}](tg://user?id={user.id})\n"
                    f"🛍 **Bot:** {bot_details['bot_name']}\n"
                    f"💎 **Plan:** {plan_name}\n"
                    f"📄 **Status:** `Pending Approval`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Approve", callback_data=f"vfy_{user.id}_{bot_id}_{plan_name}")],
                [InlineKeyboardButton("❌ Decline", callback_data=f"dcl_{user.id}_{bot_id}_{plan_name}")]
            ])
        )

        await verification_msg.delete()
        await message.reply("⏳ **Your Payment Verification Request has been sent!**\n\n"
                            "🔔 Please wait while our team verifies your payment.")

@app.on_callback_query(filters.regex(r"^(vfy|dcl)_"))
async def payment_status(client, callback_query):
    action, user_id, bot_id, plan_name = callback_query.data.split("_")
    user_id = int(user_id)

    if callback_query.from_user.id not in MODS_ID:
        return await callback_query.answer("⚠️ **You are not authorized!**", show_alert=True)

    status_text = "✅ **Payment Verified!** 🎉 Your premium plan is now activated!" if action == "vfy" else "❌ **Payment Declined!** Your plan activation was unsuccessful."
    
    await callback_query.message.delete()
    await app.send_message(user_id, text=status_text)
