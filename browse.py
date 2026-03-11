from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards import (
    browse_kb, browse_filter_kb, main_menu_kb,
    my_ad_kb, confirm_delete_kb, ad_card_kb
)
from database import (
    get_ads, get_ads_count, get_latest_ads,
    get_user_ads, delete_ad, increment_views,
    get_ad, save_ad, get_saved_ads, get_setting
)
from utils import format_ad, format_ad_compact
from config import ADS_PER_PAGE, CHANNEL_ID

router = Router()


# ── Browse ────────────────────────────────────────────────────────
@router.message(F.text == "🔍 Browse Gifts")
async def browse_gifts(msg: Message):
    await _send_browse_page(msg, page=0, category="", is_new=True)


async def _send_browse_page(target, page: int, category: str, is_new=False):
    ads   = await get_ads(category or None, page, ADS_PER_PAGE)
    total = await get_ads_count(category or None)

    if not ads:
        text = "😔 <b>No ads found.</b>\n\nBe the first to post a gift!"
        kb   = main_menu_kb() if is_new else None
        if is_new:
            return await target.answer(text, parse_mode="HTML", reply_markup=kb)
        return await target.edit_text(text, parse_mode="HTML")

    cat_label = f" in <b>{category}</b>" if category else ""
    header = (
        f"🔍 <b>Browse Gifts{cat_label}</b>\n"
        f"📊 {total} listing{'s' if total != 1 else ''} found\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    lines = "\n\n".join(format_ad_compact(a) for a in ads)
    text  = header + lines

    kb = browse_kb(page, total, category)

    if is_new:
        await target.answer(text, parse_mode="HTML", reply_markup=kb)
    else:
        await target.edit_text(text, parse_mode="HTML", reply_markup=kb)


@router.callback_query(F.data.startswith("page:"))
async def flip_page(cb: CallbackQuery):
    _, cat, page_str = cb.data.split(":")
    category = "" if cat == "all" else cat
    await _send_browse_page(cb.message, int(page_str), category, is_new=False)
    await cb.answer()


@router.callback_query(F.data == "browse:filter")
async def browse_filter(cb: CallbackQuery):
    await cb.message.edit_text(
        "📂 <b>Filter by Category</b>\n\nChoose a category:",
        parse_mode="HTML",
        reply_markup=browse_filter_kb(),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("filter:"))
async def apply_filter(cb: CallbackQuery):
    value = cb.data.split(":", 1)[1]
    if value == "back":
        await _send_browse_page(cb.message, 0, "", is_new=False)
    else:
        cat = "" if value == "all" else value
        await _send_browse_page(cb.message, 0, cat, is_new=False)
    await cb.answer()


@router.callback_query(F.data == "browse:menu")
async def browse_to_menu(cb: CallbackQuery):
    await cb.message.delete()
    await cb.message.answer("🏠 Main Menu:", reply_markup=main_menu_kb())
    await cb.answer()


# ── Latest Offers ─────────────────────────────────────────────────
@router.message(F.text == "🔥 Latest Offers")
async def latest_offers(msg: Message):
    ads = await get_latest_ads(10)
    if not ads:
        return await msg.answer(
            "😔 No offers yet. Be the first to post!",
            reply_markup=main_menu_kb()
        )
    header = (
        "🔥 <b>Latest Offers</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    lines = "\n\n".join(format_ad_compact(a) for a in ads)
    await msg.answer(header + lines, parse_mode="HTML")

    # Show last 3 as full cards with buttons
    await msg.answer("📌 <b>Top 3 Latest — Full Details:</b>", parse_mode="HTML")
    for ad in ads[:3]:
        await increment_views(ad["id"])
        await msg.answer(
            format_ad(ad),
            parse_mode="HTML",
            reply_markup=ad_card_kb(ad["id"], ad["contact"], ad["gift_link"]),
        )


# ── Save Ad ───────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("save:"))
async def save_ad_cb(cb: CallbackQuery):
    ad_id = int(cb.data.split(":")[1])
    saved = await save_ad(cb.from_user.id, ad_id)
    if saved:
        await cb.answer("❤️ Ad saved to your list!", show_alert=False)
    else:
        await cb.answer("Already saved!", show_alert=False)


@router.message(F.text == "❤️ Saved Ads")
async def saved_ads(msg: Message):
    ads = await get_saved_ads(msg.from_user.id)
    if not ads:
        return await msg.answer(
            "❤️ <b>Saved Ads</b>\n\nYou haven't saved any ads yet.\n"
            "Tap ❤️ Save on any ad to save it here!",
            parse_mode="HTML",
        )
    await msg.answer(
        f"❤️ <b>Your Saved Ads</b>  ({len(ads)} items)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML",
    )
    for ad in ads[:10]:
        await msg.answer(
            format_ad(ad),
            parse_mode="HTML",
            reply_markup=ad_card_kb(ad["id"], ad["contact"], ad["gift_link"]),
        )


# ── Ad Stats ──────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("stats:"))
async def ad_stats(cb: CallbackQuery):
    ad_id = int(cb.data.split(":")[1])
    ad = await get_ad(ad_id)
    if not ad:
        return await cb.answer("Ad not found.", show_alert=True)
    await cb.answer(
        f"📊 Ad #{ad_id}\n"
        f"👁 Views: {ad['views']}\n"
        f"📅 Posted: {ad['created_at']}",
        show_alert=True,
    )


# ── My Listings ───────────────────────────────────────────────────
@router.message(F.text == "💼 My Listings")
async def my_listings(msg: Message):
    ads = await get_user_ads(msg.from_user.id)
    if not ads:
        return await msg.answer(
            "💼 <b>My Listings</b>\n\n"
            "You haven't posted any ads yet.\n"
            "Tap 📢 Post Gift Ad to get started!",
            parse_mode="HTML",
            reply_markup=main_menu_kb(),
        )
    await msg.answer(
        f"💼 <b>My Listings</b>  ({len(ads)} ads)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML",
    )
    for ad in ads:
        await msg.answer(
            format_ad(ad),
            parse_mode="HTML",
            reply_markup=my_ad_kb(ad["id"]),
        )


@router.callback_query(F.data.startswith("del:"))
async def confirm_delete(cb: CallbackQuery):
    ad_id = int(cb.data.split(":")[1])
    await cb.message.edit_reply_markup(reply_markup=confirm_delete_kb(ad_id))
    await cb.answer("Are you sure?")


@router.callback_query(F.data.startswith("delconfirm:"))
async def do_delete(cb: CallbackQuery):
    ad_id = int(cb.data.split(":")[1])
    await delete_ad(ad_id, cb.from_user.id)
    await cb.message.edit_text(f"🗑️ <b>Ad #{ad_id} deleted.</b>", parse_mode="HTML")
    await cb.answer("Deleted!")


@router.callback_query(F.data.startswith("repost:"))
async def repost_ad(cb: CallbackQuery, bot: Bot):
    ad_id = int(cb.data.split(":")[1])
    ad = await get_ad(ad_id)
    if not ad or ad["user_id"] != cb.from_user.id:
        return await cb.answer("Ad not found.", show_alert=True)

    channel = await get_setting("channel") or CHANNEL_ID
    try:
        await bot.send_message(
            channel,
            format_ad(ad),
            parse_mode="HTML",
            reply_markup=ad_card_kb(ad["id"], ad["contact"], ad["gift_link"]),
        )
        await cb.answer("📤 Reposted to channel!", show_alert=True)
    except Exception as e:
        await cb.answer(f"Error: {e}", show_alert=True)


@router.callback_query(F.data == "noop")
async def noop(cb: CallbackQuery):
    await cb.answer()
    
# router alias for main.py import
browse_router = router
