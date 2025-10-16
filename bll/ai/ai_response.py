from bll.imports import *

from google import genai
from config.sicret import GEMINI_KEY

client = genai.Client(api_key=GEMINI_KEY)


def get_cat_ai_response(user_input: str, user_name: str):

    HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_history.json")
    PROMPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompt.txt")

    def load_chat_history(limit=20):
        """Завантажує останні `limit` повідомлень із JSON-файлу."""
        if not os.path.exists(HISTORY_FILE):
            return []
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data[-limit:] if isinstance(data, list) else []
        except Exception:
            return []

    def save_chat_message(role, text, user_name=None):
        """Додає нове повідомлення до історії."""
        history = load_chat_history(limit=1000)  # обмеження, щоб файл не розростався
        entry = {"role": role, "text": text}
        if user_name:
            entry["user_name"] = user_name
        history.append(entry)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history[-1000:], f, ensure_ascii=False, indent=2)

    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        BASE_PROMPT = f.read()

    chat_memory = load_chat_history()
    history = " | ".join(
        f"{m.get('user_name', m.get('role', ''))}: {m.get('text', '')}"
        for m in chat_memory
    ) if chat_memory else ""


    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=f"""
            {BASE_PROMPT} 

            Минулі повідомлення: {history}
            Текст від користувача{user_name}: {user_input}
            """,
        )
        text = ""
        try:
            text = response.candidates[0].content.parts[0].text
        except Exception:
            # fallback: спробуємо інші поля або просто привести response до рядка
            text = getattr(response, "output_text", "") or getattr(response, "text", "") or str(response)

        text = text.replace("*", "").strip() or "..."

        save_chat_message("user", user_input, user_name)
        save_chat_message("bot", text)

        return {"type": "text", "content": text}

    except Exception as e:
        # Лог для дебагу — дивись в логах/консолі
        print("[AI error]:", e)
        return {"type": "text", "content": "Я їм, відстань!"}
