from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from states import AdminStates
from keyboards import admin_kb, main_menu_kb
from database import (
    get_ads, get_ads_count, delete_ad, set_setting, get_setting
)

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ── Admin Panel ───────────────────────────────────────────────────
@router.message(Command("admin"))
async def admin_panel(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        return await msg.answer("❌ Access denied.")
    await state.clear()
    total = await get_ads_count()
    channel = await get_setting("channel") or "Not set"
    await msg.answer(
        f"🛠 <b>Admin Panel</b>\n\n"
        f"📊 Total active ads: <b>{total}</b>\n"
        f"📡 Channel: <code>{channel}</code>\n\n"
        f"Choose an action:",
        parse_mode="HTML",
        reply_markup=admin_kb(),
    )


# ── Set Channel ───────────────────────────────────────────────────
@router.callback_query(F.data == "admin:channel")
async def admin_set_channel(cb: CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id):
        return await cb.answer("Access denied.")
    await state.set_state(AdminStates.set_channel)
    await cb.message.edit_text(
        "📡 <b>Set Channel</b>\n\n"
        "Send the channel username or ID.\n"
        "<b>Example:</b>  <code>@mygiftchannel</code>  or  <code>-1001234567890</code>",
        parse_mode="HTML",
    )
    await cb.answer()


@router.message(AdminStates.set_channel)
async def save_channel(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        return
    channel = msg.text.strip()
    await set_setting("channel", channel)
    await state.clear()
    await msg.answer(
        f"✅ Channel set to <code>{channel}</code>",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


# ── All Ads ───────────────────────────────────────────────────────
@router.callback_query(F.data == "admin:list")
async def admin_list_ads(cb: CallbackQuery):
    if not is_admin(cb.from_user.id):
        return await cb.answer("Access denied.")
    ads = await get_ads(page=0, per_page=20)
    if not ads:
        return await cb.message.edit_text("No active ads.")
    lines = []
    for a in ads:
        lines.append(
            f"🆔 #{a['id']}  |  <b>{a['title']}</b>\n"
            f"   💰 {a['price']} {a['currency']}  |  👤 {a['contact']}  |  👁 {a['views']}"
        )
    await cb.message.edit_text(
        "📋 <b>All Active Ads</b>\n━━━━━━━━━━━━━━━━━━\n\n" + "\n\n".join(lines),
        parse_mode="HTML",
        reply_markup=admin_kb(),
    )
    await cb.answer()


# ── Delete Ad ────────────────────────────────────────────────────
@router.callback_query(F.data == "admin:delete")
async def admin_delete_prompt(cb: CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id):
        return await cb.answer("Access denied.")
    await state.set_state(AdminStates.delete_ad_id)
    await cb.message.edit_text(
        "🗑️ <b>Delete Ad</b>\n\nSend the Ad ID number:",
        parse_mode="HTML",
    )
    await cb.answer()


@router.message(AdminStates.delete_ad_id)
async def admin_do_delete(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id):
        return
    try:
        ad_id = int(msg.text.strip())
    except ValueError:
        return await msg.answer("⚠️ Please send a valid number.")
    await delete_ad(ad_id)
    await state.clear()
    await msg.answer(f"🗑️ Ad <code>#{ad_id}</code> deleted.", parse_mode="HTML")


# ── Stats ────────────────────────────────────────────────────────
@router.callback_query(F.data == "admin:stats")
async def admin_stats(cb: CallbackQuery):
    if not is_admin(cb.from_user.id):
        return await cb.answer("Access denied.")
    from config import CATEGORIES
    lines = []
    for label, value in CATEGORIES:
        count = await get_ads_count(category=value)
        lines.append(f"  {label}: <b>{count}</b>")
    total = await get_ads_count()
    channel = await get_setting("channel") or "Not set"
    await cb.message.edit_text(
        f"📊 <b>Bot Stats</b>\n\n"
        f"📡 Channel: <code>{channel}</code>\n"
        f"📦 Total ads: <b>{total}</b>\n\n"
        f"<b>By Category:</b>\n" + "\n".join(lines),
        parse_mode="HTML",
        reply_markup=admin_kb(),
    )
    await cb.answer()


# ── Broadcast ────────────────────────────────────────────────────
@router.callback_query(F.data == "admin:broadcast")
async def admin_broadcast_prompt(cb: CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id):
        return await cb.answer("Access denied.")
    await state.set_state(AdminStates.broadcast_msg)
    await cb.message.edit_text(
        "📣 <b>Broadcast</b>\n\nSend the message to broadcast to the channel:",
        parse_mode="HTML",
    )
    await cb.answer()


@router.message(AdminStates.broadcast_msg)
async def admin_do_broadcast(msg: Message, state: FSMContext, bot: Bot):
    if not is_admin(msg.from_user.id):
        return
    channel = await get_setting("channel")
    if not channel:
        await state.clear()
        return await msg.answer("⚠️ No channel set. Use /admin → Set Channel first.")
    try:
        await bot.send_message(channel, msg.text, parse_mode="HTML")
        await msg.answer("✅ Broadcast sent!")
    except Exception as e:
        await msg.answer(f"❌ Error: {e}")
    await state.clear()
    
# router alias for main.py import
admin_router = router
