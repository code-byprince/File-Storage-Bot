from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils import stats
from utils.i18n import t

def main_menu_keyboard(lang: str = "hi"):
keyboard = [
[InlineKeyboardButton(t("menu_image", lang), callback_data="menu_image")],
[InlineKeyboardButton(t("menu_document", lang), callback_data="menu_document")],
[InlineKeyboardButton(t("menu_excel", lang), callback_data="menu_excel")],
[InlineKeyboardButton(t("menu_video", lang), callback_data="menu_video")],
]
return InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
context.user_data.clear()
user = update.effective_user
stats.log_user(user.id, user.username, user.first_name)
lang = stats.get_language(user.id)
await update.message.reply_text(
t("welcome", lang), parse_mode="Markdown", reply_markup=main_menu_keyboard(lang)
)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
"Bas /start bhejo, category choose karo, phir file bhejo.\n"
f"Max file size: {context.bot_data.get('max_size_mb', 20)}MB.\n\n"
"Commands: /start /help /done /history /language /stats (admin only)"
)
