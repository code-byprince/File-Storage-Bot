from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import Config
from database import db
from utils.helpers import human_size
from plugins.start import is_subscribed, main_menu_markup, HELP_TEXT, ABOUT_TEXT, deliver_file
from plugins.myfiles import render_myfiles, render_favorites, render_recent

# store users waiting to type a new filename: {user_id: file_code}
PENDING_RENAME = {}


@Client.on_callback_query(filters.regex(r"^check_sub$"))
async def check_sub_cb(client: Client, cq: CallbackQuery):
    if await is_subscribed(client, cq.from_user.id):
        await cq.message.edit("✅ Thanks for joining! Send /start again.")
    else:
        await cq.answer("You haven't joined all channels yet.", show_alert=True)


@Client.on_callback_query(filters.regex(r"^home$"))
async def home_cb(client: Client, cq: CallbackQuery):
    text = Config.WELCOME_TEXT.format(mention=cq.from_user.mention)
    await cq.message.edit(text, reply_markup=main_menu_markup())


@Client.on_callback_query(filters.regex(r"^help$"))
async def help_cb(client: Client, cq: CallbackQuery):
    await cq.message.edit(HELP_TEXT, reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("🏠 Home", callback_data="home")]]))


@Client.on_callback_query(filters.regex(r"^about$"))
async def about_cb(client: Client, cq: CallbackQuery):
    await cq.message.edit(ABOUT_TEXT, reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("🏠 Home", callback_data="home")]]))


@Client.on_callback_query(filters.regex(r"^search_hint$"))
async def search_hint_cb(client: Client, cq: CallbackQuery):
    await cq.answer("Use /search <keyword> to search your files.", show_alert=True)


@Client.on_callback_query(filters.regex(r"^myfiles_(\d+)$"))
async def myfiles_cb(client: Client, cq: CallbackQuery):
    page = int(cq.matches[0].group(1))
    text, markup = await render_myfiles(cq.from_user.id, page)
    await cq.message.edit(text, reply_markup=markup)


@Client.on_callback_query(filters.regex(r"^favs_(\d+)$"))
async def favs_cb(client: Client, cq: CallbackQuery):
    page = int(cq.matches[0].group(1))
    text, markup = await render_favorites(cq.from_user.id, page)
    await cq.message.edit(text, reply_markup=markup)


@Client.on_callback_query(filters.regex(r"^recent_(\d+)$"))
async def recent_cb(client: Client, cq: CallbackQuery):
    page = int(cq.matches[0].group(1))
    text, markup = await render_recent(page)
    await cq.message.edit(text, reply_markup=markup)


@Client.on_callback_query(filters.regex(r"^open_(.+)$"))
async def open_file_cb(client: Client, cq: CallbackQuery):
    code = cq.matches[0].group(1)
    f = await db.get_file(code)
    if not f:
        await cq.answer("File not found.", show_alert=True)
        return
    bot_username = Config.BOT_USERNAME or (await client.get_me()).username
    link = f"https://t.me/{bot_username}?start=file_{code}"
    text = (
        f"📄 **{f['file_name']}**\n"
        f"💾 Size: {human_size(f['file_size'])}\n"
        f"📁 Category: {f.get('category', 'Documents')}\n"
        f"⬇️ Downloads: {f.get('downloads', 0)}\n"
        f"🔗 {link}"
    )
    is_owner = f["owner_id"] == cq.from_user.id
    buttons = [[InlineKeyboardButton("🔵 Download / Preview", callback_data=f"get_{code}")]]
    if is_owner or cq.from_user.id in Config.ADMINS:
        buttons.append(
            [
                InlineKeyboardButton(
                    "🟢 Unfavorite" if f.get("favorite") else "⭐ Favorite",
                    callback_data=f"fav_{code}",
                ),
                InlineKeyboardButton("🟡 Rename", callback_data=f"ren_{code}"),
                InlineKeyboardButton("🔴 Delete", callback_data=f"del_{code}"),
            ]
        )
    buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="myfiles_0")])
    await cq.message.edit(text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)


@Client.on_callback_query(filters.regex(r"^get_(.+)$"))
async def get_file_cb(client: Client, cq: CallbackQuery):
    code = cq.matches[0].group(1)
    await deliver_file(client, cq.message, code)
    await cq.answer()


@Client.on_callback_query(filters.regex(r"^fav_(.+)$"))
async def fav_cb(client: Client, cq: CallbackQuery):
    code = cq.matches[0].group(1)
    new_val = await db.toggle_favorite(code)
    if new_val is None:
        await cq.answer("File not found.", show_alert=True)
        return
    await cq.answer("⭐ Added to favorites!" if new_val else "Removed from favorites.")


@Client.on_callback_query(filters.regex(r"^del_(.+)$"))
async def delete_cb(client: Client, cq: CallbackQuery):
    code = cq.matches[0].group(1)
    f = await db.get_file(code)
    if not f:
        await cq.answer("File not found.", show_alert=True)
        return
    if f["owner_id"] != cq.from_user.id and cq.from_user.id not in Config.ADMINS:
        await cq.answer("You can't delete this file.", show_alert=True)
        return
    await db.delete_file(code)
    await cq.answer("🗑 File deleted.")
    await cq.message.edit("🗑 File deleted successfully.")


@Client.on_callback_query(filters.regex(r"^ren_(.+)$"))
async def rename_cb(client: Client, cq: CallbackQuery):
    code = cq.matches[0].group(1)
    f = await db.get_file(code)
    if not f:
        await cq.answer("File not found.", show_alert=True)
        return
    if f["owner_id"] != cq.from_user.id and cq.from_user.id not in Config.ADMINS:
        await cq.answer("You can't rename this file.", show_alert=True)
        return
    PENDING_RENAME[cq.from_user.id] = code
    await cq.answer()
    await cq.message.reply("✏️ Send me the new file name (reply as plain text):")


@Client.on_message(filters.private & filters.text & filters.create(
    lambda _, __, m: m.from_user and m.from_user.id in PENDING_RENAME
))
async def rename_text_handler(client: Client, message: Message):
    user_id = message.from_user.id
    code = PENDING_RENAME.pop(user_id)
    new_name = message.text.strip()
    await db.rename_file(code, new_name)
    await message.reply(f"✅ Renamed to **{new_name}**")
