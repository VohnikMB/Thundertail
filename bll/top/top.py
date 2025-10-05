from  bll.imports import *

STATS_FILE = 'bll/top/top_stats.json'


# ======= Допоміжні =======
def save_json(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[DEBUG] save_json error: {e}")


def load_json(path):
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except Exception as e:
            print(f"[DEBUG] load_json error: {e}")
            return {}
    return {}


# ======= Оновлення статистики =======
def update_stats(update: Update):
    """Збільшує лічильник повідомлень користувача"""
    stats = load_json(STATS_FILE)
    if not isinstance(stats, dict):
        stats = {}

    user_id = str(update.message.from_user.id)
    username = update.message.from_user.username or update.message.from_user.full_name

    if user_id not in stats:
        stats[user_id] = {"name": username, "count": 0}
    stats[user_id]["count"] += 1
    stats[user_id]["name"] = username  # оновлюємо актуальне ім’я

    save_json(STATS_FILE, stats)


# ======= Команда /top =======
async def top_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = load_json(STATS_FILE)
    if not stats:
        await update.message.reply_text("Поки що статистика пуста 📊")
        return

    sorted_users = sorted(stats.items(), key=lambda x: x[1]["count"], reverse=True)

    lines = ["🏆 Топ активних користувачів:"]
    for i, (uid, info) in enumerate(sorted_users[:10], start=1):
        lines.append(f"{i}. {info['name']} — {info['count']} повідомлень")

    await update.message.reply_text("\n".join(lines))