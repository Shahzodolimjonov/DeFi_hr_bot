from aiogram.fsm.state import StatesGroup, State


class VakansiyaForm(StatesGroup):
    kompaniya = State()
    Lavozim = State()
    maosh = State()
    Ish_turi = State()
    malumot = State()
    manzil = State()
    location = State()
    masul = State()
    status = State()


class ResumeForm(StatesGroup):
    file = State()
    description = State()
    status = State()


class UserForm(StatesGroup):
    id = State()
    telegram_id = State()
    username = State()
    vakansiyalar = State()
    resume = State()
