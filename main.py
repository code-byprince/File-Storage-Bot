import asyncio
from pyrogram import Client, idle
from config import Config
from keep_alive import keep_alive


async def main():
    keep_alive()  # starts a tiny web server so Render keeps the service alive

    app = Client(
        "FileStoreBot",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
        plugins=dict(root="plugins"),
    )

    await app.start()
    print("🤖 Bot is starting...")

    if Config.DB_CHANNEL:
        try:
            chat = await app.get_chat(Config.DB_CHANNEL)
            print(f"✅ Connected to DB channel: {chat.title} ({chat.id})")
        except Exception as e:
            print(f"⚠️ WARNING: Could not resolve DB_CHANNEL ({Config.DB_CHANNEL}): {e}")
            print(
                "➡️  Fix: forward a TEXT message from your private DB channel to the bot "
                "(as an admin, in your private chat with the bot) to get the exact ID, "
                "then update DB_CHANNEL in Render's Environment tab and redeploy."
            )

    await idle()
    await app.stop()
    print("🛑 Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
