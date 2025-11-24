import os
import sys
import logging
import asyncio

print(f"Python version: {sys.version}")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.WARNING
)

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError as e:
    print(f"Error loading telegram: {e}")
    TELEGRAM_AVAILABLE = False

try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

try:
    from googletrans import Translator
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False

# Configuration
BOT_TOKEN = "8201993248:AAF16TDh2yrEKhzrir88AQdnNsYspRwywg8"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "Translation bot is running.\n\nSend me text to translate.\n/help for help."
    await update.message.reply_text(msg)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "Help:\n"
        "/start - start the bot\n"
        "/help - show this message\n\n"
        "Send any text and I will translate it to Arabic.\n"
    )
    await update.message.reply_text(msg)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text.startswith("/"):
        return

    await update.message.reply_text("Translating...")

    try:
        if GOOGLETRANS_AVAILABLE:
            translator = Translator()
            detected = translator.detect(text)
            translation = translator.translate(text, dest="ar")
            response = f"Translation ({detected.lang} → ar):\n\n{translation.text}"
        else:
            backup = {
                "hello": "مرحبا",
                "hi": "أهلا",
                "thank you": "شكرا",
                "good morning": "صباح الخير",
                "how are you": "كيف حالك",
                "goodbye": "مع السلامة",
                "please": "من فضلك",
                "yes": "نعم",
                "no": "لا"
            }
            response = backup.get(text.lower(), f"Text: {text}")

        await update.message.reply_text(response)

    except Exception as e:
        await update.message.reply_text(f"Error while translating: {e}")



def main():
    if not TELEGRAM_AVAILABLE:
        print("Telegram library unavailable.")
        return

    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Please provide a valid bot token.")
        return

    print("Running bot...")
    application = Application.builder().token(BOT_TOKEN).build()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(application.initialize())
        print("Application initialized")
        loop.run_until_complete(application.bot.delete_webhook())
        print("Webhook deleted")
        print(f"Bot username: @{application.bot.username}")

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

        print("Bot is running.")
        try:
            loop.run_until_complete(application.run_polling(close_loop=False))
        except Exception as e:
            print(f"Polling error: {e}")

    except KeyboardInterrupt:
        print("Bot stopped.")
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")
    finally:
        loop.close()


if __name__ == "__main__":
    main()
