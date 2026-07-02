from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from database import db
from utils.helpers import human_size

PAGE_SIZE = 8


def file_list_markup(files, prefix: str, page: int, total: int):
    rows = []
    for f in files:
        star = "⭐" if f.get("favorite") else "▫️"
        rows.append(
            [InlineKeyboardButton(f"{star} {f['file_name'][:35]}", callback_data=f"open_{f['file_code']}")]
        )
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"{prefix}_{page-1}"))
    if (page + 1) * PAGE_SIZE < total:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"{prefix}_{page+1}"))
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton("🏠 Home", callback_data="home")])
    return InlineKeyboardMarkup(rows)


async def render_myfiles(user_id: int, page: int):
    total = await db.count_user_files(user_id)
    files = await db.user_files(user_id, skip=page * PAGE_SIZE, limit=PAGE_SIZE)
    if not files:
        return "📂 You haven't uploaded any files yet.", None
    text = f"📂 **My Files** ({total} total) — Page {page+1}"
    return text, file_list_markup(files, "myfiles", page, total)


async def render_favorites(user_id: int, page: int):
    total_files = await db.user_favorites(user_id, skip=0, limit=10_000)
    total = len(total_files)
    files = total_files[page * PAGE_SIZE: page * PAGE_SIZE + PAGE_SIZE]
    if not files:
        return "⭐ You have no favorite files yet.", None
    text = f"⭐ **Favorites** ({total} total) — Page {page+1}"
    return text, file_list_markup(files, "favs", page, total)


async def render_recent(page: int):
    files = await db.recent_uploads(limit=PAGE_SIZE)
    if not files:
        return "🕒 No uploads yet.", None
    text = "🕒 **Recent Uploads (global)**"
    return text, file_list_markup(files, "recent", page, len(files))


@Client.on_message(filters.command("myfiles") & filters.private)
async def myfiles_cmd(client: Client, message: Message):
    text, markup = await render_myfiles(message.from_user.id, 0)
    await message.reply(text, reply_markup=markup)


@Client.on_message(filters.command("favorites") & filters.private)
async def favorites_cmd(client: Client, message: Message):
    text, markup = await render_favorites(message.from_user.id, 0)
    await message.reply(text, reply_markup=markup)


@Client.on_message(filters.command("recent") & filters.private)
async def recent_cmd(client: Client, message: Message):
    text, markup = await render_recent(0)
    await message.reply(text, reply_markup=markup)


@Client.on_message(filters.command("search") & filters.private)
async def search_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("Usage: `/search <keyword>`")
        return
    keyword = " ".join(message.command[1:])
    results = await db.search_user_files(message.from_user.id, keyword)
    if not results:
        await message.reply("🔎 No files matched your search.")
        return
    text = f"🔎 **Search results for:** `{keyword}`"
    await message.reply(text, reply_markup=file_list_markup(results, "myfiles", 0, len(results)))


@Client.on_message(filters.command("stats") & filters.private)
async def stats_cmd(client: Client, message: Message):
    from utils.helpers import uptime

    total_u = await db.total_users()
    total_f = await db.total_files()
    storage = await db.total_storage_bytes()
    today = await db.today_uploads()
    online = await db.online_users()

    text = (
        "📊 **Bot Dashboard**\n\n"
        f"👥 Total Users: `{total_u}`\n"
        f"📁 Total Files: `{total_f}`\n"
        f"💾 Storage Used: `{human_size(storage)}`\n"
        f"📆 Today's Uploads: `{today}`\n"
        f"🟢 Online Users (10m): `{online}`\n"
        f"⏱ Bot Uptime: `{uptime()}`"
    )
    await message.reply(text)
