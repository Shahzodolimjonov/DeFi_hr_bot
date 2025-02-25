import logging
from aiogram import types, Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import async_session
from sqlalchemy.orm import Session

import content
from config import ADMIN_ID, get_db, CHANNEL_ID, SessionLocal
from keyboard import menu_kb, cancel_kb
from models.vakansiya import Vakansiya, User
from start import bot
from state import VakansiyaForm

router = Router()


def admin_kb(vacancy_id):
    buttons = [
        [InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"accept_{vacancy_id}")],
        [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{vacancy_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def get_or_create_user(user_id: int, username: str):
    async with SessionLocal() as session:
        try:
            result = await session.execute(select(User).where(User.telegram_id == user_id))
            user = result.scalars().first()
            if not user:
                user = User(telegram_id=user_id, username=username)
                session.add(user)
                await session.commit()
                await session.refresh(user)
            return user
        except Exception as e:
            print(f"Xatolik: {e}")
            return None


@router.message(F.text == content.bosh_menu)
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(content.qaytish, reply_markup=menu_kb())


@router.message(F.text == "Vakansiya")
async def start_admin_housing(message: types.Message, state: FSMContext):
    logging.info("Admin housing command received.")
    await message.answer(content.company, reply_markup=cancel_kb())
    await state.set_state(VakansiyaForm.kompaniya)


@router.message(VakansiyaForm.kompaniya)
async def add_companiya(message: types.Message, state: FSMContext):
    if not message.text.strip():
        await message.answer(content.company2)
        return
    await state.update_data(kompaniya=message.text)
    logging.info("Updated state with kompaniya: %s", message.text)
    await message.answer(content.lavozim)
    await state.set_state(VakansiyaForm.Lavozim)


@router.message(VakansiyaForm.Lavozim)
async def add_Lavozim(message: types.Message, state: FSMContext):
    if not message.text.strip():
        await message.answer(content.lavozim2)
        return
    await state.update_data(Lavozim=message.text)
    logging.info("Updated state with Lavozim: %s", message.text)
    await message.answer(content.maosh)
    await state.set_state(VakansiyaForm.maosh)


@router.message(VakansiyaForm.maosh)
async def add_maosh(message: types.Message, state: FSMContext):
    await state.update_data(maosh=message.text)
    logging.info("Updated state with maosh: %s", message.text)
    await message.answer(content.ish_turi)
    await state.set_state(VakansiyaForm.Ish_turi)


@router.message(VakansiyaForm.Ish_turi)
async def add_ish_turi(message: types.Message, state: FSMContext):
    await state.update_data(Ish_turi=message.text)
    logging.info("Updated state with malumot: %s", message.text)
    await message.answer(content.all_data)
    await state.set_state(VakansiyaForm.malumot)


@router.message(VakansiyaForm.malumot)
async def add_malumot(message: types.Message, state: FSMContext):
    await state.update_data(malumot=message.text)
    logging.info("Updated state with malumot: %s", message.text)
    await message.answer(content.manzil)
    await state.set_state(VakansiyaForm.manzil)


@router.message(VakansiyaForm.manzil)
async def add_manzil(message: types.Message, state: FSMContext):
    await state.update_data(manzil=message.text)
    logging.info("Updated state with malumot: %s", message.text)
    await message.answer(content.lakatsiya)
    await state.set_state(VakansiyaForm.location)


@router.message(VakansiyaForm.location)
async def add_location(message: types.Message, state: FSMContext):
    if message.location:
        lat, lon = message.location.latitude, message.location.longitude
        maps_url = f"https://maps.google.com/?q={lat},{lon}"
        await state.update_data(location={'latitude': lat, 'longitude': lon, 'maps_url': maps_url})
        logging.info("Updated state with location: %s", {'latitude': lat, 'longitude': lon, 'maps_url': maps_url})
    else:
        # await message.answer(content.lakatsiya2)
        await state.update_data(location=None)
        logging.info("Joylashuv koʻrsatilmagan.")
    await message.answer(content.masul)
    await state.set_state(VakansiyaForm.masul)


@router.message(VakansiyaForm.masul)
async def add_masul(message: types.Message, state: FSMContext):
    await state.update_data(masul=message.text)
    logging.info("Updated state with masul: %s", message.text)

    user_id = message.from_user.id
    username = message.from_user.username
    user = await get_or_create_user(user_id, username)
    if not user:
        await message.answer(content.save_error)
        return

    data = await state.get_data()
    required_fields = ['kompaniya', 'Lavozim', 'maosh', 'masul']
    for field in required_fields:
        if not data.get(field):
            await message.answer(f"{field} maydoni bo'sh bo'lishi mumkin emas. Iltimos, qayta kiriting.")
            return

    user_id = message.from_user.id

    async for db in get_db():
        location_data = data.get('location') or {'latitude': None, 'longitude': None, 'maps_url': '-'}
        new_vakansiya = Vakansiya(
            kompaniya=data.get('kompaniya'),
            Lavozim=data.get('Lavozim'),
            maosh=data.get('maosh'),
            Ish_turi=data.get('Ish_turi'),
            malumot=data.get('malumot'),
            manzil=data.get('manzil'),
            latitude=location_data['latitude'],
            longitude=location_data['longitude'],
            maps_url=location_data['maps_url'],
            masul=data.get('masul'),
            status="pending",
            user_id=user_id
        )

        db.add(new_vakansiya)
        await db.commit()
        await db.refresh(new_vakansiya)

    msg = (
        f"{content.Kompaniya} {data.get('kompaniya')}\n"
        f"{content.Lavozim} {data.get('Lavozim')}\n"
        f"{content.Maosh} {data.get('maosh')}\n"
        f"{content.Ish_turi} {data.get('Ish_turi')}\n"
        f"{content.Qoshimcha} {data.get('malumot')}\n"
        f"{content.Manzil} {data.get('manzil')}\n"
        f"{content.Lokatsiya} {location_data['maps_url']}\n"
        f"{content.Masul} {data.get('masul')}"
    )

    await bot.send_message(chat_id=ADMIN_ID, text=msg, reply_markup=admin_kb(new_vakansiya.id))
    await state.clear()
    await message.answer(content.moderator)


@router.callback_query(F.data.startswith("accept_"))
async def accept_vacancy(callback: CallbackQuery):
    vacancy_id = int(callback.data.split("_")[1])

    async for db in get_db():
        vakansiya = await db.execute(select(Vakansiya).filter(Vakansiya.id == vacancy_id))
        vakansiya = vakansiya.scalars().first()

        if vakansiya:
            vakansiya.status = "accepted"
            await db.commit()

            msg = (
                f"{content.Kompaniya} {vakansiya.kompaniya}\n"
                f"{content.Lavozim} {vakansiya.Lavozim}\n"
                f"{content.Ish_turi} {vakansiya.Ish_turi}\n"
                f"{content.Maosh} {vakansiya.maosh}\n"
                f"{content.Qoshimcha} {vakansiya.malumot}\n"
                f"{content.Manzil} {vakansiya.manzil}\n"
                f"{content.Lokatsiya}{vakansiya.maps_url or '-'}\n"
                f"{content.Masul} {vakansiya.masul}"
            )

            await bot.send_message(chat_id=CHANNEL_ID, text=msg)
            if vakansiya.user_id:
                await bot.send_message(chat_id=vakansiya.user_id, text=content.state)

            await callback.message.edit_text(content.cannel_save)
        else:
            await callback.message.edit_text(content.not_found)


@router.callback_query(F.data.startswith("reject_"))
async def reject_vacancy(callback: CallbackQuery):
    try:
        vacancy_id_str = callback.data.split("_")[1]
        if vacancy_id_str == "None":
            await callback.message.edit_text("⚠️Invalid vacancy ID. Please try again.")
            return

        vacancy_id = int(vacancy_id_str)
        async for db in get_db():
            vakansiya = await db.execute(select(Vakansiya).filter(Vakansiya.id == vacancy_id))
            vakansiya = vakansiya.scalars().first()

            if vakansiya:
                db.delete(vakansiya)
                db.commit()

                if vakansiya.user_id:
                    await bot.send_message(chat_id=vakansiya.user_id, text=content.error)

                await callback.message.edit_text(content.error2)
            else:
                await callback.message.edit_text(content.not_found)
    except (IndexError, ValueError) as e:
        await callback.message.edit_text(
            content.error3)
        logging.error(f"Error parsing vacancy ID: {e}")

