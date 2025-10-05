import random
from bll.imports import *

async def send_d20(update: Update, context: ContextTypes.DEFAULT_TYPE):
    images = os.listdir("bll/d20/img")
    chosen = random.choice(images)
    with open(os.path.join("bll/d20/img", chosen), "rb") as photo:
        await update.message.reply_photo(photo=photo)