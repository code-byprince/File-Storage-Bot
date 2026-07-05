import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

from config import Config
from database import db
from utils.helpers import human_size, uptime


def admin_only(func):
    async def wrapper(client: Client, message: Message):
        if message.from_user.id not in Config.ADMINS:
            await message.reply("🚫 This command is for admins only.")
            return
        await func(client, message)

    return wrapper


@Client.on_message(filters.command("admin") & filters.private)
@admin_only
async def admin_panel(client: Client, message: Message):
    text = (
        "👨‍💼 **Admin Panel**\n\n"
        "/broadcast <reply to a message> — send to all users\n"
        "/ban <user_id> — ban a user\n"
        "/unban <user_id> — unban a user\n"
        "/users — total users\n"
        "/searchfile <keyword> — search all files\n"
        "/dellog — view recent admin actions\n"
        "/stats — full dashboard\n"
    )
    await message.reply(text)


@Client.on_message(filters.command("broadcast") & filters.private)
@admin_only
async def broadcast_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply("Reply to a message with /broadcast to send it to all users.")
        return
    user_ids = await db.all_user_ids()
    sent, failed = 0, 0
    status = await message.reply(f"📢 Broadcasting to {len(user_ids)} users...")
    for uid in user_ids:
        try:
            await message.reply_to_message.copy(uid)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)  # avoid flood limits
    await db.add_log(message.from_user.id, f"Broadcast sent ({sent} ok / {failed} failed)")
    await status.edit(f"✅ Broadcast complete.\nSent: {sent}\nFailed: {failed}")


@Client.on_message(filters.command("ban") & filters.private)
@admin_only
async def ban_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("Usage: `/ban <user_id>`")
        return
    uid = int(message.command[1])
    await db.ban_user(uid)
    await db.add_log(message.from_user.id, f"Banned user {uid}")
    await message.reply(f"🚫 User `{uid}` banned.")


@Client.on_message(filters.command("unban") & filters.private)
@admin_only
async def unban_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("Usage: `/unban <user_id>`")
        return
    uid = int(message.command[1])
    await db.unban_user(uid)
    await db.add_log(message.from_user.id, f"Unbanned user {uid}")
    await message.reply(f"✅ User `{uid}` unbanned.")


@Client.on_message(filters.command("users") & filters.private)
@admin_only
async def users_cmd(client: Client, message: Message):
    total = await db.total_users()
    await message.reply(f"👥 Total Users: `{total}`")


@Client.on_message(filters.command("searchfile") & filters.private)
@admin_only
async def searchfile_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("Usage: `/searchfile <keyword>`")
        return
    keyword = " ".join(message.command[1:])
    results = await db.search_all_files(keyword)
    if not results:
        await message.reply("No files found.")
        return
    lines = [f"• {f['file_name']} ({human_size(f['file_size'])}) — owner `{f['owner_id']}`" for f in results]
    await message.reply("🔎 **Search Results:**\n\n" + "\n".join(lines))


@Client.on_message(filters.command("dellog") & filters.private)
@admin_only
async def logs_cmd(client: Client, message: Message):
    logs = await db.get_logs()
    if not logs:
        await message.reply("No admin logs yet.")
        return
    lines = [f"• `{l['admin_id']}` — {l['action']} — {l['time'].strftime('%Y-%m-%d %H:%M')}" for l in logs]
    await message.reply("📝 **Admin Logs:**\n\n" + "\n".join(lines))


@Client.on_message(filters.private & filters.forwarded & filters.text)
@admin_only
async def get_channel_id_cmd(client: Client, message: Message):
    """Admin forwards a TEXT message FROM the private DB channel to this bot,
    and the bot replies with the exact channel ID Pyrogram recognizes."""
    if message.forward_from_chat:
        chat = message.forward_from_chat
        await message.reply(
            f"✅ **Channel Detected!**\n\n"
            f"📛 Name: {chat.title}\n"
            f"🆔 ID: `{chat.id}`\n\n"
            f"👉 Copy this exact ID and put it in your `DB_CHANNEL` environment variable on Render, "
            f"then redeploy."
        )
    else:
        await message.reply(
            "⚠️ This doesn't look like a forward from a channel. "
            "Please forward a message directly from your private DB channel to me."
        )
