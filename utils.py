from config import CATEGORIES


CATEGORY_LABELS = {v: l for l, v in CATEGORIES}

# ── Beautiful Ad Card ────────────────────────────────────────────
def format_ad(ad: dict, full=True) -> str:
    cat_label = CATEGORY_LABELS.get(ad["category"], ad["category"])
    badge = _rarity_badge(ad["category"])

    header = (
        f"{badge}\n"
        f"<b>┌─────────────────────────┐</b>\n"
        f"<b>│  🎁  GIFT FOR SALE  🎁  │</b>\n"
        f"<b>└─────────────────────────┘</b>\n"
    )

    body = (
        f"\n📌 <b>{ad['title']}</b>\n\n"
        f"📂 <b>Category:</b>  {cat_label}\n"
        f"💰 <b>Price:</b>     <code>{ad['price']} {ad['currency']}</code>\n"
    )

    if full:
        desc = ad.get("description") or "—"
        body += (
            f"\n📝 <b>Description:</b>\n"
            f"<i>{desc}</i>\n\n"
            f"🔗 <b>Gift Link:</b>  <code>{ad['gift_link']}</code>\n"
            f"👤 <b>Contact:</b>    {ad['contact']}\n"
        )

    footer = (
        f"\n<b>━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        f"📅 <i>{ad['created_at']}</i>  •  "
        f"👁 <i>{ad.get('views', 0)} views</i>  •  "
        f"🆔 <i>#{ad['id']}</i>"
    )

    return header + body + footer


def format_ad_compact(ad: dict) -> str:
    cat_label = CATEGORY_LABELS.get(ad["category"], ad["category"])
    return (
        f"{'━'*28}\n"
        f"🎁 <b>{ad['title']}</b>\n"
        f"   {cat_label}  |  <code>{ad['price']} {ad['currency']}</code>\n"
        f"   👁 {ad.get('views',0)}  •  🆔 #{ad['id']}"
    )


def format_preview(data: dict) -> str:
    """Preview during wizard (no ID/views yet)."""
    cat_label = CATEGORY_LABELS.get(data.get("category",""), data.get("category","?"))
    desc = data.get("description") or "<i>No description</i>"
    return (
        f"✨ <b>Ad Preview</b> ✨\n\n"
        f"<b>┌─────────────────────────┐</b>\n"
        f"<b>│  🎁  GIFT FOR SALE  🎁  │</b>\n"
        f"<b>└─────────────────────────┘</b>\n\n"
        f"📌 <b>{data.get('title','?')}</b>\n\n"
        f"📂 <b>Category:</b>  {cat_label}\n"
        f"💰 <b>Price:</b>     <code>{data.get('price','?')} {data.get('currency','?')}</code>\n\n"
        f"📝 <b>Description:</b>\n<i>{desc}</i>\n\n"
        f"🔗 <b>Gift Link:</b>  <code>{data.get('gift_link','?')}</code>\n"
        f"👤 <b>Contact:</b>    {data.get('contact','?')}\n\n"
        f"<b>━━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        f"<i>Review your ad then tap ✅ Post Ad</i>"
    )


def _rarity_badge(category: str) -> str:
    badges = {
        "collectible": "💎 ═══ C O L L E C T I B L E ═══ 💎",
        "limited":     "🌟 ═════ L I M I T E D ══════ 🌟",
        "rare":        "🔥 ════════ R A R E ═════════ 🔥",
        "premium":     "👑 ══════ P R E M I U M ═════ 👑",
        "stars":       "⭐ ═══════ S T A R S ════════ ⭐",
        "regular":     "🎁 ═══════ G I F T ══════════ 🎁",
    }
    return badges.get(category, "🎁 ═══════ G I F T ══════════ 🎁")


# ── Welcome ──────────────────────────────────────────────────────
WELCOME_MSG = """
╔══════════════════════════════╗
║  🎁  G I F T  T R A D E R   ║
║       P R O  B O T  🤖       ║
╚══════════════════════════════╝

👋 Welcome, <b>{name}</b>!

The <b>#1 marketplace</b> to buy, sell \
& advertise Telegram Gifts.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📢  <b>Post Ad</b>    — List your gift for sale
🔍  <b>Browse</b>     — Explore all listings
🔥  <b>Latest</b>     — Freshest offers
💼  <b>My Listings</b>— Manage your ads
❤️  <b>Saved</b>      — Your saved gifts
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tap a button below to get started ↓
"""

HELP_MSG = """
📖 <b>How to use GiftTrader Pro</b>

<b>1️⃣ Post an Ad</b>
  ↳ Tap <code>📢 Post Gift Ad</code>
  ↳ Follow the step-by-step wizard
  ↳ Your ad posts to our channel!

<b>2️⃣ Browse Gifts</b>
  ↳ Tap <code>🔍 Browse Gifts</code>
  ↳ Filter by category
  ↳ Contact sellers directly

<b>3️⃣ Latest Offers</b>
  ↳ Tap <code>🔥 Latest Offers</code>
  ↳ See the 10 newest listings

<b>4️⃣ Manage your Ads</b>
  ↳ Tap <code>💼 My Listings</code>
  ↳ Delete or repost any ad

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 <b>Tips for better ads:</b>
• Use a clear, descriptive title
• Add a valid gift link (t.me/nft/...)
• Set a fair price to sell faster
• Include your @username as contact
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
