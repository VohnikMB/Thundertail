from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram_api import start_command, error_handler, handle_message

from sicret import BOT_TOKEN

if __name__ == "__main__":
    print("Starting Telegram Bot")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_error_handler(error_handler)

    app.run_polling(poll_interval=1)