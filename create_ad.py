from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import AdWizard
from keyboards import (
    category_kb, currency_kb, preview_kb,
    edit_choice_kb, skip_kb, main_menu_kb, ad_card_kb
)
from database import create_ad, get_setting
from utils import format_preview, format_ad
from config import CHANNEL_ID

router = Router()


# ── Step 1: Title ────────────────────────────────────────────────
@router.message(F.text == "📢 Post Gift Ad")
async def start_wizard(msg: Message, state: FSMContext):
    await state.clear()
    await state.set_state(AdWizard.title)
    await msg.answer(
        "📢 <b>Create Gift Ad</b>  —  Step 1 of 7\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📌 <b>Enter the Gift Title</b>\n\n"
        "<i>Give your gift a short, eye-catching name.</i>\n\n"
        "<b>Examples:</b>\n"
        "• Dragon Fire Gift Box\n"
        "• Rare Space Cat #144\n"
        "• Limited Gold Crown Gift",
        parse_mode="HTML",
        reply_markup=_cancel_kb(),
    )


@router.message(AdWizard.title)
async def got_title(msg: Message, state: FSMContext):
    if len(msg.text) > 80:
        return await msg.answer("⚠️ Title too long (max 80 chars). Try again:")
    await state.update_data(title=msg.text)
    await state.set_state(AdWizard.category)
    await msg.answer(
        "✅ Title saved!\n\n"
        "📢 <b>Create Gift Ad</b>  —  Step 2 of 7\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📂 <b>Select a Category</b>",
        parse_mode="HTML",
        reply_markup=category_kb(),
    )


# ── Step 2: Category ─────────────────────────────────────────────
@router.callback_query(F.data.startswith("cat:"), AdWizard.category)
async def got_category(cb: CallbackQuery, state: FSMContext):
    category = cb.data.split(":", 1)[1]
    await state.update_data(category=category)
    await state.set_state(AdWizard.gift_link)
    await cb.message.edit_text(
        "✅ Category selected!\n\n"
        "📢 <b>Create Gift Ad</b>  —  Step 3 of 7\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔗 <b>Send the Gift Link</b>\n\n"
        "<i>Paste the Telegram gift link or NFT link.</i>\n\n"
        "<b>Examples:</b>\n"
        "• <code>t.me/nft/DragonFire-144</code>\n"
        "• <code>https://t.me/gifts/...</code>",
        parse_mode="HTML",
    )
    await cb.answer()


# ── Step 3: Gift Link ────────────────────────────────────────────
@router.message(AdWizard.gift_link)
async def got_gift_link(msg: Message, state: FSMContext):
    link = msg.text.strip()
    await state.update_data(gift_link=link)
    await state.set_state(AdWizard.price)
    await msg.answer(
        "✅ Gift link saved!\n\n"
        "📢 <b>Create Gift Ad</b>  —  Step 4 of 7\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "💰 <b>Enter the Price</b>\n\n"
        "<i>Type a number (you'll pick currency next).</i>\n\n"
        "<b>Examples:</b>  <code>5000</code>  /  <code>12.5</code>  /  <code>250</code>",
        parse_mode="HTML",
    )


# ── Step 4: Price ────────────────────────────────────────────────
@router.message(AdWizard.price)
async def got_price(msg: Message, state: FSMContext):
    price_str = msg.text.strip().replace(",", "")
    try:
        float(price_str)
    except ValueError:
        return await msg.answer("⚠️ Please enter a valid number (e.g. <code>5000</code>):", parse_mode="HTML")
    await state.update_data(price=price_str)
    await state.set_state(AdWizard.currency)
    await msg.answer(
        "✅ Price saved!\n\n"
        "📢 <b>Create Gift Ad</b>  —  Step 5 of 7\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "💱 <b>Select Currency</b>",
        parse_mode="HTML",
        reply_markup=currency_kb(),
    )


# ── Step 5: Currency ─────────────────────────────────────────────
@router.callback_query(F.data.startswith("cur:"), AdWizard.currency)
async def got_currency(cb: CallbackQuery, state: FSMContext):
    currency = cb.data.split(":", 1)[1]
    await state.update_data(currency=currency)
    await state.set_state(AdWizard.description)
    await cb.message.edit_text(
        "✅ Currency selected!\n\n"
        "📢 <b>Create Gift Ad</b>  —  Step 6 of 7\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📝 <b>Add a Description</b>\n\n"
        "<i>Tell buyers about your gift — condition, details, why it's special.</i>\n"
        "<i>Max 500 characters.</i>",
        parse_mode="HTML",
        reply_markup=skip_kb("skip:description"),
    )
    await cb.answer()


# ── Step 6: Description ──────────────────────────────────────────
@router.callback_query(F.data == "skip:description", AdWizard.description)
async def skip_description(cb: CallbackQuery, state: FSMContext):
    await state.update_data(description="")
    await _ask_contact(cb.message, state, edit=True)
    await cb.answer()


@router.message(AdWizard.description)
async def got_description(msg: Message, state: FSMContext):
    if len(msg.text) > 500:
        return await msg.answer("⚠️ Description too long (max 500 chars). Try again:")
    await state.update_data(description=msg.text)
    await _ask_contact(msg, state, edit=False)


async def _ask_contact(target, state: FSMContext, edit=False):
    await state.set_state(AdWizard.contact)
    text = (
        "✅ Description saved!\n\n"
        "📢 <b>Create Gift Ad</b>  —  Step 7 of 7\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📞 <b>Enter Contact Info</b>\n\n"
        "<i>Your Telegram @username or a link buyers can reach you on.</i>\n\n"
        "<b>Example:</b>  <code>@yourusername</code>"
    )
    if edit:
        await target.edit_text(text, parse_mode="HTML")
    else:
        await target.answer(text, parse_mode="HTML")


# ── Step 7: Contact → Preview ────────────────────────────────────
@router.message(AdWizard.contact)
async def got_contact(msg: Message, state: FSMContext):
    contact = msg.text.strip()
    await state.update_data(contact=contact)
    await state.set_state(AdWizard.preview)

    data = await state.get_data()
    await msg.answer(
        format_preview(data),
        parse_mode="HTML",
        reply_markup=preview_kb(),
    )


# ── Preview Actions ───────────────────────────────────────────────
@router.callback_query(F.data == "post:confirm", AdWizard.preview)
async def post_ad(cb: CallbackQuery, state: FSMContext, bot: Bot):
    data   = await state.get_data()
    user   = cb.from_user
    username = f"@{user.username}" if user.username else user.full_name

    ad_id = await create_ad(
        user_id     = user.id,
        username    = user.username,
        title       = data["title"],
        category    = data["category"],
        gift_link   = data["gift_link"],
        price       = data["price"],
        currency    = data["currency"],
        description = data.get("description", ""),
        contact     = data["contact"],
    )

    # Fetch the full ad back for proper formatting
    from database import get_ad
    ad = await get_ad(ad_id)

    # Post to channel
    channel = await get_setting("channel") or CHANNEL_ID
    card_text = format_ad(ad)
    card_kb   = ad_card_kb(ad_id, ad["contact"], ad["gift_link"])

    try:
        await bot.send_message(channel, card_text, parse_mode="HTML", reply_markup=card_kb)
        channel_note = f"✅ Posted to channel {channel}!"
    except Exception as e:
        channel_note = f"⚠️ Could not post to channel: {e}"

    await state.clear()
    await cb.message.edit_text(
        f"🎉 <b>Ad Posted Successfully!</b>\n\n"
        f"🆔 Ad ID: <code>#{ad_id}</code>\n"
        f"📌 Title: <b>{data['title']}</b>\n\n"
        f"{channel_note}\n\n"
        f"Manage it anytime via <b>💼 My Listings</b>.",
        parse_mode="HTML",
    )
    await cb.message.answer("🏠 Back to menu:", reply_markup=main_menu_kb())
    await cb.answer("🎉 Ad posted!")


@router.callback_query(F.data == "post:edit", AdWizard.preview)
async def edit_ad(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text(
        "✏️ <b>What would you like to edit?</b>",
        parse_mode="HTML",
        reply_markup=edit_choice_kb(),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("edit:"), AdWizard.preview)
async def handle_edit_choice(cb: CallbackQuery, state: FSMContext):
    field = cb.data.split(":", 1)[1]

    if field == "back":
        data = await state.get_data()
        await cb.message.edit_text(
            format_preview(data), parse_mode="HTML", reply_markup=preview_kb()
        )
        return await cb.answer()

    prompts = {
        "title":       ("AdWizard:title",       "📌 Enter new <b>Title</b>:"),
        "category":    ("AdWizard:category",     "📂 Select new <b>Category</b>:"),
        "gift_link":   ("AdWizard:gift_link",    "🔗 Enter new <b>Gift Link</b>:"),
        "price":       ("AdWizard:price",        "💰 Enter new <b>Price</b>:"),
        "currency":    ("AdWizard:currency",     "💱 Select new <b>Currency</b>:"),
        "description": ("AdWizard:description",  "📝 Enter new <b>Description</b>:"),
        "contact":     ("AdWizard:contact",      "📞 Enter new <b>Contact</b>:"),
    }

    state_name, prompt = prompts[field]
    await state.set_state(state_name)

    if field == "category":
        await cb.message.edit_text(prompt, parse_mode="HTML", reply_markup=category_kb())
    elif field == "currency":
        await cb.message.edit_text(prompt, parse_mode="HTML", reply_markup=currency_kb())
    else:
        await cb.message.edit_text(prompt, parse_mode="HTML")
    await cb.answer()


# After editing a field, go back to preview
@router.message(AdWizard.title)
async def edit_title(msg: Message, state: FSMContext):
    await state.update_data(title=msg.text)
    await _show_preview(msg, state)

@router.message(AdWizard.gift_link)
async def edit_link(msg: Message, state: FSMContext):
    await state.update_data(gift_link=msg.text.strip())
    await _show_preview(msg, state)

@router.message(AdWizard.price)
async def edit_price(msg: Message, state: FSMContext):
    await state.update_data(price=msg.text.strip())
    await _show_preview(msg, state)

@router.message(AdWizard.description)
async def edit_desc(msg: Message, state: FSMContext):
    await state.update_data(description=msg.text)
    await _show_preview(msg, state)

@router.message(AdWizard.contact)
async def edit_contact_field(msg: Message, state: FSMContext):
    await state.update_data(contact=msg.text.strip())
    await _show_preview(msg, state)

@router.callback_query(F.data.startswith("cat:"), AdWizard.category)
async def edit_cat_cb(cb: CallbackQuery, state: FSMContext):
    await state.update_data(category=cb.data.split(":", 1)[1])
    data = await state.get_data()
    await state.set_state(AdWizard.preview)
    await cb.message.edit_text(format_preview(data), parse_mode="HTML", reply_markup=preview_kb())
    await cb.answer()

@router.callback_query(F.data.startswith("cur:"), AdWizard.currency)
async def edit_cur_cb(cb: CallbackQuery, state: FSMContext):
    await state.update_data(currency=cb.data.split(":", 1)[1])
    data = await state.get_data()
    await state.set_state(AdWizard.preview)
    await cb.message.edit_text(format_preview(data), parse_mode="HTML", reply_markup=preview_kb())
    await cb.answer()


async def _show_preview(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.set_state(AdWizard.preview)
    await msg.answer(format_preview(data), parse_mode="HTML", reply_markup=preview_kb())


# ── Cancel ───────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("cancel:"), AdWizard)
async def cancel_wizard(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("❌ <b>Ad creation cancelled.</b>", parse_mode="HTML")
    await cb.message.answer("🏠 Back to menu:", reply_markup=main_menu_kb())
    await cb.answer()


@router.callback_query(F.data == "post:cancel", AdWizard.preview)
async def cancel_from_preview(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text("❌ <b>Ad cancelled.</b>", parse_mode="HTML")
    await cb.message.answer("🏠 Back to menu:", reply_markup=main_menu_kb())
    await cb.answer()


def _cancel_kb():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel:menu")]
    ])
-e 
# router alias for main.py import
create_router = router
