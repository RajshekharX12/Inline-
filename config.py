import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN   = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS   = list(map(int, os.getenv("ADMIN_IDS", "123456789").split(",")))
CHANNEL_ID  = os.getenv("CHANNEL_ID", "@your_channel")   # where ads are posted
DB_PATH     = os.getenv("DB_PATH", "gifts.db")

# ── Bot personality ──────────────────────────────────────────────
BOT_NAME    = "GiftTrader Pro"
BOT_VERSION = "1.0"

# ── Pagination ───────────────────────────────────────────────────
ADS_PER_PAGE = 5

# ── Gift categories ──────────────────────────────────────────────
CATEGORIES = [
    ("💎 Collectible",  "collectible"),
    ("🌟 Limited",      "limited"),
    ("🎁 Regular",      "regular"),
    ("⭐ Stars",        "stars"),
    ("🔥 Rare",         "rare"),
    ("👑 Premium",      "premium"),
]

# ── Currencies ───────────────────────────────────────────────────
CURRENCIES = [
    ("⭐ Stars",  "Stars"),
    ("💎 TON",    "TON"),
    ("💵 USDT",   "USDT"),
    ("🤝 Trade",  "Trade"),
]
