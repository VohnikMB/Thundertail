import os, random
from collections import defaultdict, deque

from telegram import Update
from google import genai
from telegram.ext import (
    CallbackQueryHandler,
    ContextTypes,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    filters,
)

from sicret import *


# --- Команди --- #
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ти не з мого клану!")


# --- AI --- #
client = genai.Client(api_key=GEMINI_KEY)

music = [
    "https://music.youtube.com/watch?v=SOT1vOCJpLY",
    "https://music.youtube.com/watch?v=dAGU-BzlLh8",
    "https://music.youtube.com/watch?v=pl0qSJ9sdLI",
    "https://music.youtube.com/watch?v=9RfVp-GhKfs",
    "https://music.youtube.com/watch?v=cYT325Fe9zU",
    "https://music.youtube.com/watch?v=0LuignGmX_0",
    "https://music.youtube.com/watch?v=Ni3ofdKfamI",
    "https://music.youtube.com/watch?v=9RfVp-GhKfs",
    "https://music.youtube.com/watch?v=W49Is2Py3FQ",
    "https://music.youtube.com/watch?v=Y9ftyP9XPEM",
    "https://music.youtube.com/watch?v=_vUN731Wn_s"
]


def get_cat_ai_response(user_input: str, chat_memory) -> str:
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=f"""
            Ти — кіт-воїн зі світу Cat Warriors. Твоє ім’я Thundertail або Шандер чи Гром, Громохвіст, для друзів.  
            Твій характер: саркастичний, дотепний і трохи різкуватий, але добрий усередині. Ти любиш поговорити. 
            Ти можеш підколоти співрозмовника, пожартувати чи відповісти з іронією, але ніколи не буваєш по-справжньому злим.  
            Ти завжди лишаєшся відданим своєму клану і підтримуєш тих, кого вважаєш друзями.  
            Говори коротко, емоційно і в стилі справжнього воїна-кота.  
            Не пояснюй правила, не розкривай що ти бот — просто грай роль.  
            Якщо співрозмовник звертається до тебе, відповідай так, ніби він кіт з того ж світу.  
            Уникай сучасної людської тематики (комп’ютери, інтернет, машини) — існує тільки світ котів-воїнів, природа, кланове життя та їхні закони.  
            Минулі повідомлення: {" | ".join([m["text"] for m in chat_memory])}
            Текст від користувача: {user_input}
            """,
        )

        return response.candidates[0].content.parts[0].text.replace("*", "").strip()
    except Exception as e:
        print("AI error:", e)
        return "Я їм, відстань!"


def get_ai_response(user_input: str) -> str:
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=f""" Ти віртуальний помічник. Давай розширені і інформативні відповіді.
            Текст від користувача: {user_input}
            """,
        )

        return response.candidates[0].content.parts[0].text.strip()
    except Exception as e:
        print("AI error:", e)
        return "Я їм, відстань!"


def cat_response(text: str, chat_id: int, chat_memory):
    processed: str = text.lower()

    if "music" in processed or "музика" in processed or "музику" in processed:
        return {"type": "text", "content": random.choice(music)}

    if "джеміні" in processed or "genai" in processed or "gemini" in processed:
        return {"type": "text", "content": get_ai_response(text)}

    if "d20" in processed or "д20" in processed:
        images = os.listdir("d20")
        chosen = random.choice(images)
        return {"type": "image", "path": os.path.join("d20", chosen)}

    return {"type": "text", "content": get_cat_ai_response(text, chat_memory[chat_id])}


# --- Обробка повідомлень --- #
chat_memory = defaultdict(lambda: deque(maxlen=40))


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f"User({chat_id}) in {message_type}: {text}")

    if message_type in ["group", "supergroup"]:
        if chat_id != CHAT_ID:
            return

        if (
            BOT_USERNAME in text
            or "Thunder" in text
            or "Шандер" in text
            or "Хвостатий" in text
            or "Гром" in text
            or "Громохвіст" in text
        ):
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            chat_memory[chat_id].append({"user_id": user_id, "text": text})
            response = cat_response(new_text, chat_id, chat_memory)
        else:
            return
    else:  # приватний чат
        if user_id != MY_USER_ID:
            return
        chat_memory[chat_id].append({"user_id": user_id, "text": text})
        response = cat_response(text, chat_id, chat_memory)

    print("Bot", response)

    if isinstance(response, dict) and response.get("type") == "image":
        with open(response["path"], "rb") as photo:
            await update.message.reply_photo(photo)
    elif isinstance(response, dict) and response.get("type") == "text":
        await update.message.reply_text(response["content"])
    else:
        await update.message.reply_text(str(response))


# --- Логування помилок --- #
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")
