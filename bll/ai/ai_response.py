import os

from google import genai
from config.sicret import GEMINI_KEY

client = genai.Client(api_key=GEMINI_KEY)


def get_cat_ai_response(user_input: str, chat_memory):
    history = " | ".join(m.get("text", "") for m in chat_memory) if chat_memory else ""

    PROMPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompt.txt")

    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        BASE_PROMPT = f.read()

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=f"""
            {BASE_PROMPT} 

            Минулі повідомлення: {history}
            Текст від користувача: {user_input}
            """,
        )
        text = ""
        try:
            text = response.candidates[0].content.parts[0].text
        except Exception:
            # fallback: спробуємо інші поля або просто привести response до рядка
            text = getattr(response, "output_text", "") or getattr(response, "text", "") or str(response)

        text = text.replace("*", "").strip()
        if not text:
            text = "..."  # щоб не повернути пусте

        return {"type": "text", "content": text}

    except Exception as e:
        # Лог для дебагу — дивись в логах/консолі
        print("[AI error]:", e)
        return {"type": "text", "content": "Я їм, відстань!"}
