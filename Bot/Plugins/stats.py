from Bot import app, MODS_ID
from pyrogram import filters
from Bot.Database import get_users_list

@app.on_message(filters.command(["stats"]))
async def stats_command(client, message):
    if message.from_user.id not in MODS_ID:
        return   
    users = len(await get_users_list())
    await message.reply(f"**✨ --Bot Stats-- :**\n\n**👥 Users :** `{users}`")
