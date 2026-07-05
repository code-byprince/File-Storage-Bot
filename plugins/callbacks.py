from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from handlers.file_handler import PARAM_PROMPTS, DIRECT_PROMPTS
from utils import stats
from utils.i18n import t

IMAGE_MENU = [
[InlineKeyboardButton("→ JPG", callback_data="action_img_to_jpg"),
InlineKeyboardButton("→ PNG", callback_data="action_img_to_png")],
[InlineKeyboardButton("→ WEBP", callback_data="action_img_to_webp"),
InlineKeyboardButton("Compress", callback_data="action_img_compress")],
[InlineKeyboardButton("Resize", callback_data="action_img_resize")],
[InlineKeyboardButton("Images → PDF", callback_data="action_img_to_pdf")],
[InlineKeyboardButton("PDF → Images", callback_data="action_pdf_to_img")],
[InlineKeyboardButton("⬅️ Back", callback_data="menu_main")],
]

DOCUMENT_MENU = [
[InlineKeyboardButton("PDF → Text", callback_data="action_pdf_to_text")],
[InlineKeyboardButton("Text → PDF", callback_data="action_text_to_pdf")],
[InlineKeyboardButton("PDF → Word", callback_data="action_pdf_to_word")],
[InlineKeyboardButton("Word → PDF", callback_data="action_word_to_pdf")],
[InlineKeyboardButton("Merge PDFs", callback_data="action_pdf_merge"),
InlineKeyboardButton("Split PDF", callback_data="action_pdf_split")],
[InlineKeyboardButton("Add Password", callback_data="action_pdf_add_password"),
InlineKeyboardButton("Remove Password", callback_data="action_pdf_remove_password")],
[InlineKeyboardButton("⬅️ Back", callback_data="menu_main")],
]

EXCEL_MENU = [
[InlineKeyboardButton("Excel → CSV", callback_data="action_excel_to_csv")],
[InlineKeyboardButton("CSV → Excel", callback_data="action_csv_to_excel")],
[InlineKeyboardButton("⬅️ Back", callback_data="menu_main")],
]

VIDEO_MENU = [
[InlineKeyboardButton("Video → MP3", callback_data="action_vid_to_audio")],
[InlineKeyboardButton("Video Compress", callback_data="action_vid_compress")],
[InlineKeyboardButton("⬅️ Back", callback_data="menu_main")],
]

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
try:
await query.answer()
except BadRequest:

Bot Render pe "so" raha tha, callback bahut der se process hua aur

Telegram ka query expire ho gaya - ignore karo, button ka kaam phir bhi ho jayega

pass
data = query.data

if data == "menu_main":
from handlers.start import main_menu_keyboard
context.user_data.clear()
lang = stats.get_language(update.effective_user.id)
await query.edit_message_text(t("welcome", lang), parse_mode="Markdown",
reply_markup=main_menu_keyboard(lang))
return

if data == "menu_image":
await query.edit_message_text("🖼️ Image Tools — kya karna hai?", parse_mode="Markdown",
reply_markup=InlineKeyboardMarkup(IMAGE_MENU))
return

if data == "menu_document":
await query.edit_message_text("📄 Document Tools — kya karna hai?", parse_mode="Markdown",
reply_markup=InlineKeyboardMarkup(DOCUMENT_MENU))
return

if data == "menu_excel":
await query.edit_message_text("📊 Excel/CSV Tools — kya karna hai?", parse_mode="Markdown",
reply_markup=InlineKeyboardMarkup(EXCEL_MENU))
return

if data == "menu_video":
await query.edit_message_text("🎬 Video/Audio Tools — kya karna hai?", parse_mode="Markdown",
reply_markup=InlineKeyboardMarkup(VIDEO_MENU))
return

Actions jo pehle text parameter maangte hain (resize dims, password, split range)

if data in PARAM_PROMPTS:
param_key, prompt_text = PARAM_PROMPTS[data]
context.user_data["awaiting_param"] = param_key
context.user_data["pending_action"] = None
await query.edit_message_text(f"✍️ {prompt_text}")
return

Actions jo seedhe file maangte hain

if data in DIRECT_PROMPTS:
context.user_data["pending_action"] = data
context.user_data["awaiting_param"] = None
context.user_data["collected_images"] = []
context.user_data["collected_pdfs"] = []
await query.edit_message_text(f"✅ {DIRECT_PROMPTS[data]}")
return
