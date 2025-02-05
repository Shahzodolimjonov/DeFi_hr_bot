import logging
import os
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import ADMIN_ID, get_db, CHANNEL_ID, SessionLocal
from keyboard import menu_kb, cancel_kb, inline_kb
from models.vakansiya import Resume, User
from start import bot
from state import ResumeForm

router = Router()


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
            logging.error(f"Foydalanuvchi olishda/yaratishda xatolik: {e}")
            return None


async def get_user_by_telegram_id(user_id: int):
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        return result.scalars().first()


@router.message(F.text == "🔙 Bekor qilish")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Qaytish", reply_markup=menu_kb())


@router.message(F.text == "Resume")
async def start_admin_resume(message: Message, state: FSMContext):
    logging.info("Admin resume command received.")
    await message.answer("Resume faylini kiriting:", reply_markup=cancel_kb())
    await state.set_state(ResumeForm.file)


@router.message(ResumeForm.file)
async def handle_resume(message: Message, state: FSMContext):
    if not message.document:
        await message.answer("Iltimos, fayl yuboring.")
        return

    file_id = message.document.file_id
    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path

    directory = "resumes"
    os.makedirs(directory, exist_ok=True)
    destination = os.path.join(directory, message.document.file_name)

    await bot.download_file(file_path, destination)
    await state.update_data(file=destination)
    await state.set_state(ResumeForm.description)

    await message.answer("Rezyume qabul qilindi. Endi qo'shimcha ma'lumot kiriting.")


@router.message(ResumeForm.description)
async def handle_description(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    user = await get_or_create_user(user_id, username)

    if not user:
        await message.answer("❌ Foydalanuvchi ma'lumotlarini saqlashda xatolik yuz berdi.")
        return

    user_data = await state.get_data()
    file_path = user_data.get("file")

    if not file_path:
        await message.answer("❌ Fayl yo'qolgan yoki noto'g'ri holat.")
        await state.clear()
        return

    caption = message.text or ""

    async with SessionLocal() as session:
        new_resume = Resume(file_path=file_path, description=caption, user_id=user_id)
        session.add(new_resume)
        await session.commit()
        await session.refresh(new_resume)

        await state.update_data(resume_id=new_resume.id)

    resume_caption = f"Rezyume fayli\nID: {new_resume.id}"

    await bot.send_document(
        chat_id=ADMIN_ID,
        document=FSInputFile(file_path),
        caption=resume_caption,
        reply_markup=inline_kb()
    )
    await message.answer("Rezyume va qo'shimcha ma'lumot adminlarga yuborildi.")


@router.callback_query(F.data.in_(["accept", "reject"]))
async def handle_resume_review(callback: CallbackQuery):
    caption = callback.message.caption

    if not caption:
        await callback.answer("❌ Xabar caption (izoh) yo‘q.")
        return

    if "ID:" not in caption:
        await callback.answer(f"❌ Rezyume ID topilmadi.\nCaption: {caption}")
        return

    try:
        resume_id = int(caption.split("ID:")[-1].strip())
    except ValueError:
        await callback.answer(f"❌ Rezyume ID noto‘g‘ri formatda.\nCaption: {caption}")
        return

    async with SessionLocal() as session:
        resume = await session.get(Resume, resume_id)
        if not resume:
            await callback.answer(f"❌ Rezyume topilmadi. ID: {resume_id}")
            return

        new_status = "accepted" if callback.data == "accept" else "rejected"
        resume.status = new_status
        await session.commit()

        user_result = await session.execute(select(User).filter(User.telegram_id == resume.user_id))
        user = user_result.scalar()
        if user:
            status_text = "✅ Rezyumeingiz qabul qilindi." if new_status == "accepted" else "❌ Rezyume rad etildi."
            await bot.send_message(chat_id=user.telegram_id, text=status_text)

        if new_status == "accepted":
            try:
                await bot.forward_message(chat_id=CHANNEL_ID, from_chat_id=callback.message.chat.id, message_id=callback.message.message_id)
            except Exception as e:
                logging.error(f"Error forwarding message to channel: {e}")
                await callback.answer("❌ Rezyume kanalga yuborishda xatolik yuz berdi.")
        else:
            try:
                await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
            except Exception as e:
                logging.error(f"Error deleting message: {e}")
                await callback.answer("❌ Rezyume xabarini o'chirishda xatolik yuz berdi.")

        await callback.answer("Holat yangilandi.")
        # await callback.message.edit_reply_markup(reply_markup=None)

