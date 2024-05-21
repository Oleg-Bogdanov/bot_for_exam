import json
from config import BOT_TOKEN_PATH

def get_bot_token():
    with open(BOT_TOKEN_PATH, 'r') as f:
        return f.read().strip()
