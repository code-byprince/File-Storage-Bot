from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from utils import stats
from utils.i18n import t

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
user_id = update.effective_user.id
lang = stats.get_language(user_id)
keyboard = [
[InlineKeyboardButton("🇮🇳 Hindi (Hinglish)", callback_data="lang_hi"),
InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
]
await update.message.reply_text(t("lang_choose", lang), reply_markup=InlineKeyboardMarkup(keyboard))

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
try:
await query.answer()
except BadRequest:
pass  # Query expire ho gaya (bot cold-start se so raha tha), ignore karo
user_id = update.effective_user.id
lang = "hi" if query.data == "lang_hi" else "en"
stats.set_language(user_id, lang)
await query.edit_message_text(t("lang_set", lang))
