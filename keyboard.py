from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton


def menu_kb():
    kb = [
        [
            KeyboardButton(text="Resume"),
            KeyboardButton(text="Vakansiya")
        ],
    ]

    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Tanlang"
    )

    return keyboard


def cancel_kb():
    kb = [
        [
            KeyboardButton(text="🔙 Bosh Menu")
        ]
    ]

    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
    )

    return keyboard


def inline_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="☑ Accept", callback_data="accept"),
            InlineKeyboardButton(text="✖ Reject", callback_data="reject")
        ]
    ]
    )
    return kb
