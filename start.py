from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from keyboards import main_menu_kb
from utils import WELCOME_MSG, HELP_MSG

router = Router()


@router.message(CommandStart())
async def cmd_start(msg: Message, state: FSMContext):
    await state.clear()
    name = msg.from_user.full_name
    await msg.answer(
        WELCOME_MSG.format(name=name),
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


@router.message(Command("menu"))
@router.message(F.text == "🔙 Main Menu")
async def cmd_menu(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "🏠 <b>Main Menu</b>\n\nChoose an option below 👇",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )


@router.message(F.text == "ℹ️ Help")
async def cmd_help(msg: Message):
    await msg.answer(HELP_MSG, parse_mode="HTML")


# router alias for main.py import
start_router = router
