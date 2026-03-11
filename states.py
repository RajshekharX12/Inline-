from aiogram.fsm.state import State, StatesGroup


class AdWizard(StatesGroup):
    title    = State()
    category = State()
    gift_link = State()
    price    = State()
    currency = State()
    description = State()
    contact  = State()
    preview  = State()


class AdminStates(StatesGroup):
    set_channel   = State()
    broadcast_msg = State()
    delete_ad_id  = State()
