# handlers.py
# ──────────────────────────────────────────────────────────────────────────────
# Все взаимодействие с пользователем: опрос → генерация маршрута → кнопки

import asyncio
import datetime
import os

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup
from fastapi import BackgroundTasks

from config       import TELEGRAM_TOKEN
from db           import db, Route, User
from openai_helper import generate_itinerary, edit_day
from states       import TripStates
from utils        import itinerary_keyboard, edit_day_keyboard, split_message

router = Router()           # подключается в bot_init.py


# ──────────────────────────────── 1. Опрос пользователя
@router.message(CommandStart())
async def cmd_start(m: types.Message, st: FSMContext):
    await st.set_state(TripStates.waiting_days)
    await m.answer("🗓️ На сколько дней ты планируешь поездку в Токио?")

@router.message(TripStates.waiting_days)
async def step_days(m: types.Message, st: FSMContext):
    if not m.text.isdigit():
        return await m.answer("Введите число цифрами.")
    await st.update_data(days=m.text)
    await st.set_state(TripStates.waiting_travelers)
    await m.answer("👥 Кто едет с тобой?")

@router.message(TripStates.waiting_travelers)
async def step_travelers(m: types.Message, st: FSMContext):
    await st.update_data(travelers=m.text)
    await st.set_state(TripStates.waiting_interests)
    await m.answer("🎌 Основные интересы?")

@router.message(TripStates.waiting_interests)
async def step_interests(m: types.Message, st: FSMContext):
    await st.update_data(interests=m.text)
    await st.set_state(TripStates.waiting_pace)
    await m.answer("🚶‍♂️ Предпочтительный темп? (спокойный/умеренный/активный)")

@router.message(TripStates.waiting_pace)
async def step_pace(m: types.Message, st: FSMContext):
    await st.update_data(pace=m.text)
    await st.set_state(TripStates.waiting_budget)
    await m.answer("💴 Бюджет на день? (экономный/средний/высокий)")

@router.message(TripStates.waiting_budget)
async def step_budget(m: types.Message, st: FSMContext):
    await st.update_data(budget=m.text)
    await st.set_state(TripStates.waiting_food)
    await m.answer("🍱 Предпочтения по еде?")

@router.message(TripStates.waiting_food)
async def step_food(m: types.Message, st: FSMContext):
    await st.update_data(food=m.text)
    await st.set_state(TripStates.waiting_special_requests)
    await m.answer("📌 Есть особые пожелания или ограничения?")

# ──────────────────────────────── 2. Генерация маршрута
@router.message(TripStates.waiting_special_requests)
async def step_special(
    m: types.Message,
    st: FSMContext,
    background_tasks: BackgroundTasks | None = None
):
    await st.update_data(special_requests=m.text)
    data = await st.get_data()               # все ответы пользователя
    await m.answer("⏳ Генерирую маршрут… (~1‑2 мин)")
    await st.clear()                         # опрос завершён

    uid, cid = m.from_user.id, m.chat.id
    if background_tasks:                     # webhook‑режим (FastAPI)
        background_tasks.add_task(generate_and_send_itinerary, uid, cid, data)
    else:                                    # polling‑режим
        asyncio.create_task(generate_and_send_itinerary(uid, cid, data))


async def generate_and_send_itinerary(user_id: int, chat_id: int, data: dict):
    """Фоновая генерация + отправка маршрута"""
    bot = Bot(token=TELEGRAM_TOKEN, parse_mode="Markdown")
    try:
        itinerary = await generate_itinerary(data)

        # сохраняем в БД
        with db:
            User.get_or_create(user_id=user_id)
            Route.create(
                user        = user_id,
                name        = f"Маршрут {datetime.datetime.now():%d.%m %H:%M}",
                itinerary   = itinerary,
                created_at  = datetime.datetime.now()
            )

        # дробим длинный текст и отправляем
        parts = split_message(itinerary)
        for part in parts[:-1]:
            await bot.send_message(chat_id, part)
        await bot.send_message(chat_id, parts[-1], reply_markup=itinerary_keyboard())

    except Exception as e:
        await bot.send_message(chat_id, f"⚠️ Ошибка: {e}")
    finally:
        await bot.session.close()


# ──────────────────────────────── 3. Кнопка «Экспорт в PDF»
@router.callback_query(F.data == "export_pdf")
async def export_pdf(cb: types.CallbackQuery):
    with db:
        route = (Route
                 .select()
                 .where(Route.user == cb.from_user.id)
                 .order_by(Route.created_at.desc())
                 .first())

    if not route:
        return await cb.answer("Маршрут не найден.")

    # простая PDF‑генерация (через reportlab)
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet

    filename = f"itinerary_{cb.from_user.id}.pdf"
    doc = SimpleDocTemplate(filename)
    story = [Paragraph(route.itinerary, getSampleStyleSheet()["Normal"])]
    doc.build(story)

    await cb.message.answer_document(FSInputFile(filename))
    os.remove(filename)
    await cb.answer("Готово ✅")


# ──────────────────────────────── 4. Кнопка «Редактировать день»
@router.callback_query(F.data == "edit_day")
async def edit_day_menu(cb: types.CallbackQuery):
    with db:
        route = (Route.select()
                 .where(Route.user == cb.from_user.id)
                 .order_by(Route.created_at.desc())
                 .first())

    if not route:
        return await cb.answer("Маршрут не найден.")

    await cb.message.answer(
        "Выбери день для редактирования:",
        reply_markup=edit_day_keyboard(route.itinerary)
    )
    await cb.answer()


@router.callback_query(F.data.startswith("edit_specific_day_"))
async def ask_edit(cb: types.CallbackQuery, st: FSMContext):
    day = cb.data.split("_")[-1]
    await st.update_data(day_to_edit=day)
    await st.set_state(TripStates.editing_day)
    await cb.message.answer(f"✏️ Что изменить в Дне {day}?")
    await cb.answer()


@router.message(TripStates.editing_day)
async def apply_edit(m: types.Message, st: FSMContext):
    data = await st.get_data()
    day  = data["day_to_edit"]

    with db:
        route = (Route.select()
                 .where(Route.user == m.from_user.id)
                 .order_by(Route.created_at.desc())
                 .first())
    if not route:
        await st.clear()
        return await m.answer("Маршрут не найден.")

    new_text = await edit_day(route.itinerary, day, m.text)
    route.itinerary = new_text
    route.save()

    for part in split_message(new_text)[:-1]:
        await m.answer(part)
    await m.answer(split_message(new_text)[-1], reply_markup=itinerary_keyboard())
    await st.clear()


# ──────────────────────────────── 5. Кнопка «Удалить маршрут»
@router.callback_query(F.data == "delete_route")
async def delete_route_menu(cb: types.CallbackQuery):
    with db:
        routes = (Route.select()
                  .where(Route.user == cb.from_user.id)
                  .order_by(Route.created_at.desc()))
    if not routes.exists():
        return await cb.answer("Маршрутов нет.")

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(f"🗑 {r.name}", callback_data=f"del_{r.id}")]
            for r in routes
        ]
    )
    await cb.message.answer("Выбери маршрут для удаления:", reply_markup=kb)
    await cb.answer()


@router.callback_query(F.data.startswith("del_"))
async def delete_route(cb: types.CallbackQuery):
    rid = int(cb.data.split("_")[-1])
    with db:
        route = Route.get_or_none(Route.id == rid, Route.user == cb.from_user.id)
        if not route:
            return await cb.answer("Маршрут не найден.")
        name = route.name
        route.delete_instance()
    await cb.message.answer(f"✅ Удалён «{name}».")
    await cb.answer()


# ──────────────────────────────── 6. Команда /cancel
@router.message(Command("cancel"))
async def cancel(m: types.Message, st: FSMContext):
    await st.clear()
    await m.answer("Действие отменено. /start — начать сначала.")
