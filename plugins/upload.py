import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import Config
from database import db
from utils.helpers import encode_code, human_size, detect_category
from plugins.start import is_subscribed, force_sub_markup


def extract_file_info(message: Message):
    """Returns (file_type, file_name, file_size, file_unique_id)."""
    if message.document:
        d = message.document
        return "document", d.file_name or "document", d.file_size, d.file_unique_id
    if message.video:
        v = message.video
        return "video", v.file_name or "video.mp4", v.file_size, v.file_unique_id
    if message.audio:
        a = message.audio
        return "audio", a.file_name or "audio.mp3", a.file_size, a.file_unique_id
    if message.voice:
        v = message.voice
        return "voice", "voice_message.ogg", v.file_size, v.file_unique_id
    if message.photo:
        p = message.photo
        return "photo", "photo.jpg", p.file_size, p.file_unique_id
    return None, None, None, None


@Client.on_message(
    filters.private
    & (filters.document | filters.video | filters.audio | filters.voice | filters.photo)
)
async def handle_upload(client: Client, message: Message):
    user = message.from_user
    if await db.is_banned(user.id):
        await message.reply("🚫 You are banned from using this bot.")
        return

    if not await is_subscribed(client, user.id):
        await message.reply(
            "🔒 Please join our channel(s) first.", reply_markup=force_sub_markup()
        )
        return

    file_type, file_name, file_size, file_unique_id = extract_file_info(message)
    if not file_type:
        return

    status = await message.reply("⏳ Uploading & generating permanent link...")

    try:
        copied = await message.copy(chat_id=Config.DB_CHANNEL)
    except Exception as e:
        await status.edit(f"❌ Upload failed: {e}")
        return

    code = encode_code(copied.id)
    category = detect_category(file_type, file_name)

    await db.save_file(
        {
            "file_code": code,
            "db_msg_id": copied.id,
            "owner_id": user.id,
            "file_name": file_name,
            "file_size": file_size or 0,
            "file_type": file_type,
            "category": category,
            "favorite": False,
            "downloads": 0,
            "uploaded_at": datetime.datetime.utcnow(),
        }
    )

    bot_username = Config.BOT_USERNAME or (await client.get_me()).username
    link = f"https://t.me/{bot_username}?start=file_{code}"

    caption = (
        f"✅ **File Stored Successfully!**\n\n"
        f"📄 **Name:** {file_name}\n"
        f"💾 **Size:** {human_size(file_size or 0)}\n"
        f"📁 **Category:** {category}\n\n"
        f"🔗 **Permanent Link:**\n{link}"
    )

    markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔗 Share Link", switch_inline_query=link)],
            [
                InlineKeyboardButton("⭐ Favorite", callback_data=f"fav_{code}"),
                InlineKeyboardButton("✏️ Rename", callback_data=f"ren_{code}"),
                InlineKeyboardButton("🗑 Delete", callback_data=f"del_{code}"),
            ],
        ]
    )
    await status.edit(caption, reply_markup=markup, disable_web_page_preview=True)
