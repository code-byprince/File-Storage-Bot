from pyrogram import Client
from config import Config
from keep_alive import keep_alive

if __name__ == "__main__":
    keep_alive()  # starts a tiny web server so Render keeps the service alive

    app = Client(
        "FileStoreBot",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
        plugins=dict(root="plugins"),
    )

    print("🤖 Bot is starting...")
    app.run()
    print("🛑 Bot stopped.")
