import random

from bll.ai.ai_response import get_cat_ai_response
from bll.imports import *
from bll.setting import is_private_chat, CHAT_ID, BOT_USERNAME, is_group_chat, MY_USER_ID, CHAT_ID2
from bll.top.top import update_stats
from collections import defaultdict, deque

chat_memory = defaultdict(lambda: deque(maxlen=40))

# Константи
KEYWORDS_FILE = 'bll/media/keywords.json'


# ======= Допоміжні функції =======
def save_keywords(data):
    try:
        with open(KEYWORDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("[DEBUG] keywords.json -- записано успішно")
    except Exception as e:
        print(f"[DEBUG] save_keywords error: {e}")


def load_keywords():
    if os.path.exists(KEYWORDS_FILE):
        try:
            with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except Exception as e:
            print(f"[DEBUG] load_keywords error: {e}")
            return []
    return []


def generate_id(data):
    if not data:
        return 1
    return max(item.get("id", 0) for item in data) + 1


# ======= Команди =======

# Додавання
async def add_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_private_chat(update) or user_id != MY_USER_ID:
        return

    if not context.args:
        await update.message.reply_text(
            "Формат:\n"
            "1) Відповідь на фото/відео/гіф/стікер з ключовими словами:\n"
            "   /media_respond кіт, котик\n"
         )
        return

    keywords = [k.strip().lower() for k in ' '.join(context.args).split(',')]
    media_msg = update.message.reply_to_message

    entry = {"id": None, "keywords": keywords}

    if media_msg:  # якщо є reply
        if media_msg.photo:
            entry["type"] = "photo"
            entry["file_id"] = media_msg.photo[-1].file_id
        elif media_msg.video:
            entry["type"] = "video"
            entry["file_id"] = media_msg.video.file_id
        elif media_msg.animation:
            entry["type"] = "animation"
            entry["file_id"] = media_msg.animation.file_id
        elif media_msg.sticker:
            entry["type"] = "sticker"
            entry["file_id"] = media_msg.sticker.file_id
        else:
            await update.message.reply_text("Цей тип медіа не підтримується.")
            return

        if media_msg.caption:
            entry["caption"] = media_msg.caption
    else:
        entry["type"] = "text"
        entry["content"] = ' '.join(context.args)

    data = load_keywords()
    new_id = generate_id(data)
    entry["id"] = new_id
    data.append(entry)
    save_keywords(data)

    await update.message.reply_text(f"✅ Додано! ID = {new_id}")


# Видалення
async def delete_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_private_chat(update) or user_id != MY_USER_ID:
        return

    if not context.args:
        await update.message.reply_text("Вкажи ID для видалення. Наприклад: /delete_respond 2")
        return

    try:
        media_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("ID має бути числом.")
        return

    data = load_keywords()
    entry = next((x for x in data if x.get("id") == media_id), None)

    if not entry:
        await update.message.reply_text(f"❌ Запис з ID {media_id} не знайдено.")
        return

    data = [x for x in data if x.get("id") != media_id]
    save_keywords(data)

    await update.message.reply_text(f"🗑 Запис з ID {media_id} видалено.")

import re

# Відповідь за ключовим словом
async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    if not is_group_chat(update):
        return

    chat_id = update.effective_chat.id
    text = update.message.text.lower()
    user_id = update.effective_user.id

    print(f"[DEBUG] on_message called: chat_id={chat_id}, user={user_id}, text={text[:200]}")

    data = load_keywords()
    update_stats(update)

    # Більш надійний пошук ключових слів (word boundary)
    def keyword_in_text(keyword, text_):
        return re.search(r'\b' + re.escape(keyword.lower()) + r'\b', text_) is not None

    matched = [entry for entry in data if any(keyword_in_text(k, text) for k in entry.get('keywords', []))]

    if matched:
        chosen = random.choice(matched)
        media_type = chosen.get('type')
        try:
            if media_type == "photo":
                await update.message.reply_photo(chosen['file_id'], caption=chosen.get("caption"))
            elif media_type == "video":
                await update.message.reply_video(chosen['file_id'], caption=chosen.get("caption"))
            elif media_type == "animation":
                await update.message.reply_animation(chosen['file_id'], caption=chosen.get("caption"))
            elif media_type == "sticker":
                await update.message.reply_sticker(chosen['file_id'])
            elif media_type == "text":
                await update.message.reply_text(chosen.get('content', ''))
        except Exception as e:
            print("[DEBUG] send media error:", e)
            await update.message.reply_text(f"⚠️ Помилка відправки: {e}")

    # ================= AI-блок (групи) =================
    message_type: str = update.message.chat.type
    if message_type in ["group", "supergroup"]:
        print(f"User({chat_id}) in {message_type}: {text}")

        if chat_id not in [CHAT_ID, CHAT_ID2]:
            return

        bot_name = (BOT_USERNAME or "").lower().lstrip('@')
        triggers = [t for t in [bot_name, "thunder", "шандер", "хвостатий", "гром", "громохвіст"] if t]

        # --- Перевірка згадки ---
        mentioned = False
        if getattr(update.message, "entities", None):
            for ent in update.message.entities:
                if ent.type in ("mention", "text_mention"):
                    ent_text = update.message.text[ent.offset: ent.offset + ent.length].lower()
                    if bot_name and bot_name in ent_text:
                        mentioned = True
                        break

        # --- НОВЕ: перевірка, чи це відповідь на бота ---
        replied_to_bot = (
                update.message.reply_to_message
                and update.message.reply_to_message.from_user
                and update.message.reply_to_message.from_user.is_bot
        )

        if any(t in text for t in triggers) or mentioned or replied_to_bot:
            new_text = text
            if bot_name:
                new_text = new_text.replace(bot_name, "").strip()
            if not new_text:
                new_text = text  # fallback

            chat_memory[chat_id].append({"user_id": user_id, "text": new_text})

            try:
                response = get_cat_ai_response(new_text, chat_memory[chat_id])
                if isinstance(response, dict) and response.get("type") == "text":
                    await update.message.reply_text(response["content"])
                elif isinstance(response, str):
                    await update.message.reply_text(response)
                else:
                    await update.message.reply_text(str(response))
            except Exception as e:
                print("[DEBUG] AI send error:", e)
                await update.message.reply_text("⚠️ Помилка при обробці AI.")
