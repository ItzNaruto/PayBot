import asyncio
from Bot import app, MODS_ID
from pyrogram import filters
from pyrogram.enums import ParseMode
from Bot.Database import get_users_list

BROADCAST_SLEEP = 1

@app.on_message(filters.command(["bcast", "broadcast"]))
async def broadcast(_, message):
    if message.from_user.id not in MODS_ID:
        return

    if not message.reply_to_message:
        return await message.reply_text(
            "🔄 **Reply to a message to send a broadcast!**\n"
            "💡 This will copy your message to all users."
        )

    to_send = message.reply_to_message.id
    users = await get_users_list() or []

    failed_users = 0

    for user in users:
        try:
            await app.copy_message(chat_id=int(user), from_chat_id=message.chat.id, message_id=to_send)
            await asyncio.sleep(BROADCAST_SLEEP)
        except Exception:
            failed_users += 1

    await message.reply_text(
        f"📢 **Broadcast Results**\n\n"
        f"✅ **Users Delivered:** `{len(users) - failed_users}`\n"
        f"❌ **Users Failed:** `{failed_users}`\n\n"
        f"✨ Broadcast successfully completed!"
    )

