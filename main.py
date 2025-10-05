from telegram.ext import Application, CommandHandler, MessageHandler, filters
from bll.d20.d20_call import send_d20
from config.sicret import BOT_TOKEN
from bll.media.media_resend import add_image, delete_image, on_message
from bll.top.top import top_users

if __name__ == '__main__':
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('media_respond', add_image))
    app.add_handler(CommandHandler('delete_respond', delete_image))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
    app.add_handler(CommandHandler('top', top_users))
    app.add_handler(CommandHandler('d20', send_d20))


    print("🤖 Бот запущено...")
    app.run_polling()
