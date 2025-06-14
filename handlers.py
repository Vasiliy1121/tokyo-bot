from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from states import TripStates
from openai_helper import generate_itinerary, edit_day
from utils import itinerary_keyboard, edit_day_keyboard
from utils import split_message
from db import db, User, Route
import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from pdf_export import itinerary_to_pdf
import os

router = Router()
user_itineraries = {}  # хранилище маршрутов пользователей

# 🚩 Команда старт
@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(TripStates.waiting_days)
    await message.answer("🗓️ На сколько дней ты планируешь поездку в Токио?")

# Сбор количества дней
@router.message(TripStates.waiting_days)
async def get_days(message: types.Message, state: FSMContext):
    await state.update_data(days=message.text)
    await state.set_state(TripStates.waiting_travelers)
    await message.answer("👥 Кто едет с тобой? (один, пара, семья с детьми, друзья…)")

# Сбор состава путешественников
@router.message(TripStates.waiting_travelers)
async def get_travelers(message: types.Message, state: FSMContext):
    await state.update_data(travelers=message.text)
    await state.set_state(TripStates.waiting_interests)
    await message.answer("🎌 Какие твои основные интересы в Токио?")

# Сбор интересов
@router.message(TripStates.waiting_interests)
async def get_interests(message: types.Message, state: FSMContext):
    await state.update_data(interests=message.text)
    await state.set_state(TripStates.waiting_pace)
    await message.answer("🚶‍♂️ Какой темп тебе нравится? (спокойный, умеренный или активный)")

# Сбор темпа
@router.message(TripStates.waiting_pace)
async def get_pace(message: types.Message, state: FSMContext):
    await state.update_data(pace=message.text)
    await state.set_state(TripStates.waiting_budget)
    await message.answer("💴 Какой у тебя бюджет на день? (экономный, средний, высокий)")

# Сбор бюджета
@router.message(TripStates.waiting_budget)
async def get_budget(message: types.Message, state: FSMContext):
    await state.update_data(budget=message.text)
    await state.set_state(TripStates.waiting_food)
    await message.answer("🍱 Какие предпочтения по еде? (японская кухня, вегетарианство, аллергии, морепродукты)")

# Сбор предпочтений по еде
@router.message(TripStates.waiting_food)
async def get_food(message: types.Message, state: FSMContext):
    await state.update_data(food=message.text)
    await state.set_state(TripStates.waiting_special_requests)
    await message.answer("📌 Есть ли особые пожелания или ограничения?")

# Сбор особых пожеланий и генерация маршрута
@router.message(TripStates.waiting_special_requests)
async def get_special_requests(message: types.Message, state: FSMContext):
    await state.update_data(special_requests=message.text)
    data = await state.get_data()

    await message.answer("⏳ Пожалуйста, подожди примерно 1–2 минуты — я генерирую твой подробный маршрут по Токио…")

    try:
        itinerary = await generate_itinerary(data)

        # Сохраняем маршрут с уникальным названием
        itinerary_entry = {
            'name': f"Маршрут от {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
            'itinerary': itinerary
        }

        # Сохранение в базу SQLite
        db.connect()
        user, created = User.get_or_create(user_id=message.from_user.id)

        Route.create(
            user=user,
            name=f"Маршрут от {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
            itinerary=itinerary,
            created_at=datetime.datetime.now()
        )
        db.close()

        messages = split_message(itinerary)

        for part in messages[:-1]:
            await message.answer(part, parse_mode="Markdown")

        await message.answer(messages[-1], reply_markup=itinerary_keyboard(), parse_mode="Markdown")

    except Exception as e:
        await message.answer(f"⚠️ Произошла ошибка: {e}")
        print(f"Ошибка при генерации маршрута: {e}")

    await state.clear()

# Обработка нажатия кнопки "Редактировать день"
@router.callback_query(F.data == "edit_day")
async def edit_day_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    db.connect()
    user = User.get_or_none(user_id=user_id)

    if user is None:
        await callback.answer("Маршрут не найден.")
        db.close()
        return

    itinerary_entry = Route.select().where(Route.user == user).order_by(Route.created_at.desc()).first()

    if itinerary_entry is None:
        await callback.answer("Маршрут не найден.")
        db.close()
        return

    itinerary = itinerary_entry.itinerary
    db.close()

    await callback.message.answer("Выбери день:", reply_markup=edit_day_keyboard(itinerary))
    await callback.answer()


# Обработка выбора дня для редактирования
@router.callback_query(F.data.startswith("edit_specific_day_"))
async def handle_specific_day_edit(callback: types.CallbackQuery, state: FSMContext):
    day_number = callback.data.split("_")[-1]
    user_id = callback.from_user.id

    db.connect()
    user = User.get_or_none(user_id=user_id)

    if user is None:
        await callback.answer("Маршрут не найден.")
        db.close()
        return

    itinerary_entry = Route.select().where(Route.user == user).order_by(Route.created_at.desc()).first()

    if itinerary_entry is None:
        await callback.answer("Маршрут не найден.")
        db.close()
        return

    itinerary = itinerary_entry.itinerary
    db.close()

    await state.update_data(day_to_edit=day_number, itinerary=itinerary)
    await state.set_state(TripStates.editing_day)
    await callback.message.answer(f"✏️ Что именно хочешь изменить в Дне {day_number}?")
    await callback.answer()


# Обработчик редактирования дня (получаем пожелания и формируем новый день)
@router.message(TripStates.editing_day)
async def process_edit_day(message: types.Message, state: FSMContext):
    user_input = message.text
    data = await state.get_data()
    day_to_edit = data['day_to_edit']
    user_id = message.from_user.id

    db.connect()
    user = User.get_or_none(user_id=user_id)

    if user is None:
        await message.answer("⚠️ Маршрут не найден.")
        db.close()
        await state.clear()
        return

    itinerary_entry = Route.select().where(Route.user == user).order_by(Route.created_at.desc()).first()

    if itinerary_entry is None:
        await message.answer("⚠️ Маршрут не найден.")
        db.close()
        await state.clear()
        return

    current_itinerary = itinerary_entry.itinerary

    await message.answer(f"⏳ Меняю День {day_to_edit} — это займёт около минуты…")

    try:
        new_itinerary = await edit_day(current_itinerary, day_to_edit, user_input)

        # Обновляем маршрут в базе
        itinerary_entry.itinerary = new_itinerary
        itinerary_entry.save()

        db.close()

        messages = split_message(new_itinerary)

        for part in messages[:-1]:
            await message.answer(part, parse_mode="Markdown")

        await message.answer(messages[-1], reply_markup=itinerary_keyboard(), parse_mode="Markdown")

    except Exception as e:
        await message.answer(f"⚠️ Произошла ошибка: {e}")
        print(f"Ошибка при редактировании дня: {e}")
        db.close()

    await state.clear()



# Обработка команд /cancel или сброса
@router.message(Command("cancel"))
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🔄 Действие отменено. Чтобы начать заново, нажми /start.")

@router.message(Command("my_routes"))
async def show_saved_routes(message: types.Message):
    user_id = message.from_user.id

    db.connect()
    user = User.get_or_none(user_id=user_id)

    if user is None:
        await message.answer("📌 У тебя пока нет сохранённых маршрутов.")
        db.close()
        return

    routes = Route.select().where(Route.user == user).order_by(Route.created_at.desc())

    if not routes.exists():
        await message.answer("📌 У тебя пока нет сохранённых маршрутов.")
        db.close()
        return

    buttons = [
        [InlineKeyboardButton(text=route.name, callback_data=f"show_route_{route.id}")]
        for route in routes
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer("📌 Твои сохранённые маршруты:", reply_markup=keyboard)
    db.close()



@router.callback_query(F.data.startswith("show_route_"))
async def handle_show_route(callback: types.CallbackQuery):
    route_id = int(callback.data.split("_")[-1])

    db.connect()
    route = Route.get_or_none(Route.id == route_id)

    if route is None:
        await callback.answer("⚠️ Маршрут не найден.")
        db.close()
        return

    itinerary = route.itinerary
    messages = split_message(itinerary)

    for part in messages[:-1]:
        await callback.message.answer(part, parse_mode="Markdown")

    await callback.message.answer(messages[-1], reply_markup=itinerary_keyboard(), parse_mode="Markdown")
    db.close()
    await callback.answer()


@router.message(Command("delete_route"))
async def delete_route_command(message: types.Message):
    user_id = message.from_user.id
    itineraries = user_itineraries.get(user_id, [])

    if not itineraries:
        await message.answer("📌 У тебя пока нет маршрутов для удаления.")
        return

    buttons = [
        [InlineKeyboardButton(text=f"🗑️ {itinerary['name']}", callback_data=f"delete_route_{idx}")]
        for idx, itinerary in enumerate(itineraries)
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer("🗑️ Выбери маршрут, который хочешь удалить:", reply_markup=keyboard)

@router.message(Command("export_pdf"))
async def export_pdf(message: types.Message):
    user_id = message.from_user.id

    db.connect()
    user = User.get_or_none(user_id=user_id)

    if user is None:
        await message.answer("⚠️ Маршрут не найден.")
        db.close()
        return

    itinerary_entry = Route.select().where(Route.user == user).order_by(Route.created_at.desc()).first()

    if itinerary_entry is None:
        await message.answer("⚠️ Маршрут не найден.")
        db.close()
        return

    itinerary_text = itinerary_entry.itinerary
    db.close()

    pdf_filename = f"itinerary_{user_id}.pdf"
    itinerary_to_pdf(itinerary_text, pdf_filename)

    pdf_file = FSInputFile(pdf_filename)  # правильно упаковываем файл для отправки
    await message.answer_document(pdf_file)

    os.remove(pdf_filename)  # удаляем файл после отправки


@router.callback_query(F.data.startswith("delete_route_"))
async def handle_delete_route(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    idx = int(callback.data.split("_")[-1])

    itineraries = user_itineraries.get(user_id, [])

    if idx >= len(itineraries):
        await callback.answer("⚠️ Маршрут не найден.")
        return

    deleted_name = itineraries.pop(idx)['name']
    await callback.message.answer(f"✅ Маршрут «{deleted_name}» удалён.")
    await callback.answer()

@router.message(Command("export_pdf"))
async def export_pdf(message: types.Message):
    user_id = message.from_user.id

    db.connect()
    user = User.get_or_none(user_id=user_id)

    if user is None:
        await message.answer("⚠️ Маршрут не найден.")
        db.close()
        return

    itinerary_entry = Route.select().where(Route.user == user).order_by(Route.created_at.desc()).first()

    if itinerary_entry is None:
        await message.answer("⚠️ Маршрут не найден.")
        db.close()
        return

    itinerary_text = itinerary_entry.itinerary
    db.close()

    pdf_filename = f"itinerary_{user_id}.pdf"
    itinerary_to_pdf(itinerary_text, pdf_filename)

    with open(pdf_filename, "rb") as pdf_file:
        await message.answer_document(pdf_file)

    os.remove(pdf_filename)  # удаляем файл после отправки
