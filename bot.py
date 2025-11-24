import os
import sys
import logging
import tempfile
import asyncio

print(f"Python version: {sys.version}")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
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
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    from googletrans import Translator
    translator = Translator()
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False
    translator = None

BOT_TOKEN = "8201993248:AAF16TDh2yrEKhzrir88AQdnNsYspRwywg8"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "Translation bot is running.\n\nSend me text to translate.\n"
    if TESSERACT_AVAILABLE:
        msg += "You can also send an image with text.\n"
    msg += "/help for help."
    await update.message.reply_text(msg)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "Help:\n"
        "/start - start the bot\n"
        "/help - show this message\n\n"
        "How to use:\n"
        "1. Send any text and I will translate it to Arabic.\n"
    )
    if TESSERACT_AVAILABLE:
        msg += "2. You can send an image with text and I will extract it."
    await update.message.reply_text(msg)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text.startswith("/"):
        return

    await update.message.reply_text("Translating...")

    try:
        if GOOGLETRANS_AVAILABLE and translator:
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


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not TESSERACT_AVAILABLE:
        await update.message.reply_text("Image text extraction not available.")
        return

    await update.message.reply_text("Processing image...")

    try:
        file = await update.message.photo[-1].get_file()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
            await file.download_to_drive(temp.name)
            image = Image.open(temp.name)
            extracted = pytesseract.image_to_string(image, lang="eng+ara").strip()

        os.unlink(temp.name)

        if not extracted:
            await update.message.reply_text("No text found in the image.")
            return

        response = f"Extracted text:\n{extracted}"

        if GOOGLETRANS_AVAILABLE and translator:
            translated = translator.translate(extracted, dest="ar")
            response += f"\n\nTranslation:\n{translated.text}"

        await update.message.reply_text(response)

    except Exception as e:
        await update.message.reply_text(f"Error processing image: {e}")


async def main_async():
    if not TELEGRAM_AVAILABLE:
        print("Telegram library unavailable.")
        return

    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Please provide a valid bot token.")
        return

    print("Running bot...")
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    if TESSERACT_AVAILABLE and PILLOW_AVAILABLE:
        application.add_handler(MessageHandler(filters.PHOTO, handle_image))
        print("Image processing enabled.")

    print("Bot is running.")
    await application.run_polling()


def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("Bot stopped.")
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
