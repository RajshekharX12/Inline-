from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from config import CATEGORIES, CURRENCIES, ADS_PER_PAGE


# ── Main Menu ────────────────────────────────────────────────────
def main_menu_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(
        KeyboardButton(text="📢 Post Gift Ad"),
        KeyboardButton(text="🔍 Browse Gifts"),
    )
    kb.row(
        KeyboardButton(text="🔥 Latest Offers"),
        KeyboardButton(text="💼 My Listings"),
    )
    kb.row(
        KeyboardButton(text="❤️ Saved Ads"),
        KeyboardButton(text="ℹ️ Help"),
    )
    return kb.as_markup(resize_keyboard=True)


def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


# ── Category Picker ──────────────────────────────────────────────
def category_kb(back_cb="menu") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for label, value in CATEGORIES:
        builder.button(text=label, callback_data=f"cat:{value}")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="❌ Cancel", callback_data=f"cancel:{back_cb}"))
    return builder.as_markup()


# ── Currency Picker ──────────────────────────────────────────────
def currency_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for label, value in CURRENCIES:
        builder.button(text=label, callback_data=f"cur:{value}")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel:menu"))
    return builder.as_markup()


# ── Ad Preview Confirm ───────────────────────────────────────────
def preview_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Post Ad",    callback_data="post:confirm"),
        InlineKeyboardButton(text="✏️ Edit",       callback_data="post:edit"),
    )
    builder.row(
        InlineKeyboardButton(text="❌ Cancel",     callback_data="post:cancel"),
    )
    return builder.as_markup()


def edit_choice_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    fields = [
        ("📌 Title",       "edit:title"),
        ("📂 Category",    "edit:category"),
        ("🔗 Gift Link",   "edit:gift_link"),
        ("💰 Price",       "edit:price"),
        ("💱 Currency",    "edit:currency"),
        ("📝 Description", "edit:description"),
        ("📞 Contact",     "edit:contact"),
    ]
    for label, cb in fields:
        builder.button(text=label, callback_data=cb)
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="🔙 Back to Preview", callback_data="edit:back"))
    return builder.as_markup()


# ── Ad Card (shown in channel / browse) ─────────────────────────
def ad_card_kb(ad_id: int, contact: str, gift_link: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if gift_link.startswith("http") or gift_link.startswith("t.me"):
        url = gift_link if gift_link.startswith("http") else f"https://{gift_link}"
        builder.row(InlineKeyboardButton(text="🎁 View Gift", url=url))
    builder.row(
        InlineKeyboardButton(text="💬 Contact Seller", url=f"https://t.me/{contact.lstrip('@')}"),
        InlineKeyboardButton(text="❤️ Save",           callback_data=f"save:{ad_id}"),
    )
    builder.row(InlineKeyboardButton(text="📊 Stats",  callback_data=f"stats:{ad_id}"))
    return builder.as_markup()


# ── Browse Pagination ────────────────────────────────────────────
def browse_kb(page: int, total: int, category: str = "") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    cat_str = category or "all"

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Prev", callback_data=f"page:{cat_str}:{page-1}"))
    nav.append(InlineKeyboardButton(text=f"📄 {page+1}/{max(1,(total+ADS_PER_PAGE-1)//ADS_PER_PAGE)}",
                                     callback_data="noop"))
    if (page + 1) * ADS_PER_PAGE < total:
        nav.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"page:{cat_str}:{page+1}"))
    if nav:
        builder.row(*nav)

    builder.row(
        InlineKeyboardButton(text="🔽 Filter Category", callback_data="browse:filter"),
        InlineKeyboardButton(text="🔙 Menu",            callback_data="browse:menu"),
    )
    return builder.as_markup()


def browse_filter_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🌐 All Gifts", callback_data="filter:all")
    for label, value in CATEGORIES:
        builder.button(text=label, callback_data=f"filter:{value}")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="filter:back"))
    return builder.as_markup()


# ── My Listings ──────────────────────────────────────────────────
def my_ad_kb(ad_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🗑️ Delete",    callback_data=f"del:{ad_id}"),
        InlineKeyboardButton(text="📤 Repost",    callback_data=f"repost:{ad_id}"),
    )
    return builder.as_markup()


def confirm_delete_kb(ad_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Yes, Delete", callback_data=f"delconfirm:{ad_id}"),
        InlineKeyboardButton(text="❌ No",           callback_data="cancel:menu"),
    )
    return builder.as_markup()


# ── Admin Panel ──────────────────────────────────────────────────
def admin_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📡 Set Channel",   callback_data="admin:channel"))
    builder.row(InlineKeyboardButton(text="📋 All Active Ads", callback_data="admin:list"))
    builder.row(InlineKeyboardButton(text="📣 Broadcast",     callback_data="admin:broadcast"))
    builder.row(InlineKeyboardButton(text="🗑️ Delete Ad by ID", callback_data="admin:delete"))
    builder.row(InlineKeyboardButton(text="📊 Stats",         callback_data="admin:stats"))
    return builder.as_markup()


def skip_kb(cb="skip") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭️ Skip", callback_data=cb)]
    ])
