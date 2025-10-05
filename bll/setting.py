from bll.imports import *
from typing import Final

CHAT_ID: Final = -1001807490957
CHAT_ID2: Final = -1001807490957

MY_USER_ID: Final = 800632151
BOT_USERNAME: Final = "@Thundertailbot"

def is_private_chat(update: Update) -> bool:
    return update.effective_chat and update.effective_chat.type == "private"

def is_group_chat(update: Update) -> bool:
    return update.message.chat.type in ("group", "supergroup")