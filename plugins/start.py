from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

from config import Config
from database import db
from utils.helpers import decode_code, human_size, uptime

async def is_subscribed(client: Client, user_id: int) -> bool:
if not Config.FORCE_SUB_CHANNELS:
return True
for channel in Config.FORCE_SUB_CHANNELS:
try:
member = await client.get_chat_member(channel, user_id)
if member.status in ("kicked", "left"):
return False
except UserNotParticipant:
return False
except Exception:
return False
return True

def force_sub_markup():
buttons = [
[InlineKeyboardButton(f"📢 Join {ch}", url=f"https://t.me/{ch}")]
for ch in Config.FORCE_SUB_CHANNELS
]
buttons.append([InlineKeyboardButton("✅ I Joined", callback_data="check_sub")])
return InlineKeyboardMarkup(buttons)

def main_menu_markup():
return InlineKeyboardMarkup(
[
[InlineKeyboardButton("📂 My Files", callback_data="myfiles_0"),
InlineKeyboardButton("⭐ Favorites", callback_data="favs_0")],
[InlineKeyboardButton("🕒 Recent Uploads", callback_data="recent_0"),
InlineKeyboardButton("🔎 Search", callback_data="search_hint")],
[InlineKeyboardButton("ℹ️ About", callback_data="about"),
InlineKeyboardButton("❓ Help", callback_data="help")],
]
)

@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
user = message.from_user
if await db.is_banned(user.id):
await message.reply("🚫 You are banned from using this bot.")
return

await db.add_user(user.id, user.username or "", user.first_name or "")  

if not await is_subscribed(client, user.id):  
    await message.reply(  
        "🔒 **Access Restricted**\n\nPlease join our channel(s) below to use this bot, "  
        "then tap **I Joined**.",  
        reply_markup=force_sub_markup(),  
    )  
    return  

# ---- Deep link file request: /start file_<code> ----  
if len(message.command) > 1 and message.command[1].startswith("file_"):  
    code = message.command[1].split("file_", 1)[1]  
    await deliver_file(client, message, code)  
    return  

text = Config.WELCOME_TEXT.format(mention=user.mention)  
if Config.START_PIC:  
    await message.reply_photo(Config.START_PIC, caption=text, reply_markup=main_menu_markup())  
else:  
    await message.reply(text, reply_markup=main_menu_markup())

async def deliver_file(client: Client, message: Message, code: str):
file_doc = await db.get_file(code)
if not file_doc:
await message.reply("❌ File not found or the link is invalid.")
return
try:
sent = await client.copy_message(
chat_id=message.chat.id,
from_chat_id=Config.DB_CHANNEL,
message_id=file_doc["db_msg_id"],
caption=(
f"📄 {file_doc['file_name']}\n"
f"💾 Size: {human_size(file_doc['file_size'])}"
),
)
await db.increment_downloads(code)
except Exception as e:
await message.reply(f"⚠️ Could not deliver file: {e}")

@Client.on_message(filters.command("help") & filters.private)
async def help_cmd(client: Client, message: Message):
await message.reply(HELP_TEXT)

@Client.on_message(filters.command("about") & filters.private)
async def about_cmd(client: Client, message: Message):
await message.reply(ABOUT_TEXT)

HELP_TEXT = """
📖 Bot Commands

• Send me any file (photo, video, audio, PDF, ZIP, APK, anything) — I'll store it and give you a permanent link.
• /myfiles — browse your uploaded files
• /search <keyword> — search your files
• /recent — recently uploaded files
• /favorites — your starred files
• /stats — bot statistics

Tap a file in My Files to get Preview, Rename, Delete, Favorite or Share options.
"""

ABOUT_TEXT = """
ℹ️ About This Bot

🤖 Advanced File Storage Bot
⚙️ Built with Pyrogram + MongoDB
☁️ Hosted 24/7 on Render
🔗 Permanent, unlimited file links
"""
