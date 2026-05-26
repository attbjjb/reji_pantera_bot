import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                           FSInputFile, CallbackQuery)
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import time
from dotenv import load_dotenv

# ==========================================
# ЗАГРУЗКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ
# ==========================================
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID не найден в переменных окружения!")

# ==========================================
# СОЗДАНИЕ БОТА
# ==========================================
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Хранилища
user_work_message = {}
user_data = {}
user_carts = {}

# ==========================================
# ЦЕНЫ НА ВИДЕО
# ==========================================
SINGLE_VIDEO_PRICE = 1390

COMBO_PRICES = {
    1: 1390,
    2: 1790,
    3: 2190,
    4: 2590,
    5: 2990,
    6: 3390,
    7: 3790,
    8: 4190,
    9: 4590
}

PRICES = {
    "video_1": SINGLE_VIDEO_PRICE,
    "video_2": SINGLE_VIDEO_PRICE,
    "video_3": SINGLE_VIDEO_PRICE,
    "video_4": SINGLE_VIDEO_PRICE,
    "video_5": SINGLE_VIDEO_PRICE,
    "video_6": SINGLE_VIDEO_PRICE,
    "video_7": SINGLE_VIDEO_PRICE,
    "video_8": SINGLE_VIDEO_PRICE,
    "video_9": SINGLE_VIDEO_PRICE
}


def calculate_total_price(selected_videos):
    video_count = len(selected_videos)
    if video_count > 9:
        total_price = COMBO_PRICES[9]
    else:
        total_price = COMBO_PRICES[video_count]
    return total_price, total_price, 0


PREVIEWS_INFO = {
    "video_1": {
        "name": "Perhaps",
        "description": "хореография с атмосферой загадки и лёгкой недосказанности. Плавная, тягучая, идеально для проработки линий.",
        "price": PRICES["video_1"],
        "preview": "videos/preview1.mp4"
    },
    "video_2": {
        "name": "Масло",
        "description": "скользящая, вязкая манера. Здесь важна текучесть и мягкость, движения будто растекаются в пространстве.",
        "price": PRICES["video_2"],
        "preview": "videos/preview2.mp4"
    },
    "video_3": {
        "name": "Paper",
        "description": "чёткая, графичная хореография с акцентами. Можно почувствовать хрусткость и лёгкую агрессию в подаче.",
        "price": PRICES["video_3"],
        "preview": "videos/preview3.mp4"
    },
    "video_4": {
        "name": "Snap",
        "description": "резкая, импульсивная связка. Быстрая смена положений, много ударов и изоляций. Энергия на максимум.",
        "price": PRICES["video_4"],
        "preview": "videos/preview4.mp4"
    },
    "video_5": {
        "name": "Цыганка",
        "description": "яркая, темпераментная хореография с фолк-вайбом. Можно прожить драйв, свободу и внутренний огонь.",
        "price": PRICES["video_5"],
        "preview": "videos/preview5.mp4"
    },
    "video_6": {
        "name": "T fest",
        "description": "дерзкая, уверенная подача под мощный бит. Подходит, если хочется почувствовать себя в центре внимания без лишней сладости.",
        "price": PRICES["video_6"],
        "preview": "videos/preview6.mp4"
    },
    "video_7": {
        "name": "Порвано",
        "description": "надломленная, чувственная хореография. Здесь есть надрыв, эмоция и немного хаоса в хорошем смысле.",
        "price": PRICES["video_7"],
        "preview": "videos/preview7.mp4"
    },
    "video_8": {
        "name": "Drake",
        "description": "плавная, напевная манера. Движения под вокал, стелиться по полу и работать с настроением «лёгкой меланхолии».",
        "price": PRICES["video_8"],
        "preview": "videos/preview8.MP4"
    },
    "video_9": {
        "name": "Yasmi",
        "description": "женственная, секси-хореография с восточным оттенком. Та самая, когда можно замедлиться, вытащить мягкость и красоту движения.",
        "price": PRICES["video_9"],
        "preview": "videos/preview9.mp4"
    }
}


class PaymentStates(StatesGroup):
    waiting_for_payment = State()
    waiting_for_phone = State()


from urllib.parse import quote


def get_main_menu_keyboard(user_id=None):
    if user_id:
        bot_username = "rejipantera_bot"
        message_text = "Привет! Посмотри онлайн-разборы хореографий от Регины!"
        bot_link = f"https://t.me/{bot_username}?start={user_id}"
        referal_link = f"https://t.me/share/url?url={quote(bot_link)}&text={quote(message_text)}"
    else:
        referal_link = "https://t.me/rejipantera_bot"

    cart_button = []
    if user_id and user_id in user_carts and user_carts[user_id]:
        cart_button = [InlineKeyboardButton(text=f"🛒 Корзина ({len(user_carts[user_id])})", callback_data="show_cart")]

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выбрать видео", callback_data="choose_video")],
        cart_button if cart_button else [],
        [InlineKeyboardButton(text="Пригласить друга", url=referal_link)]
    ])


def get_video_choice_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Perhaps", callback_data="view_video_1"),
         InlineKeyboardButton(text="Масло", callback_data="view_video_2")],
        [InlineKeyboardButton(text="Paper", callback_data="view_video_3"),
         InlineKeyboardButton(text="Snap", callback_data="view_video_4")],
        [InlineKeyboardButton(text="Цыганка", callback_data="view_video_5"),
         InlineKeyboardButton(text="T fest", callback_data="view_video_6")],
        [InlineKeyboardButton(text="Порвано", callback_data="view_video_7"),
         InlineKeyboardButton(text="Drake", callback_data="view_video_8")],
        [InlineKeyboardButton(text="Yasmi", callback_data="view_video_9")],
        [InlineKeyboardButton(text="⭐️Хочу всё", callback_data="add_all_to_cart")],
        [InlineKeyboardButton(text="Корзина", callback_data="show_cart"),
         InlineKeyboardButton(text="Назад", callback_data="back_to_main")]
    ])


def get_empty_cart_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выбрать видео", callback_data="choose_video")],
        [InlineKeyboardButton(text="Главное меню", callback_data="back_to_main")]
    ])


def get_video_view_keyboard(video_key, user_id):
    in_cart = user_id in user_carts and video_key in user_carts[user_id]

    if in_cart:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Убрать из корзины", callback_data=f"remove_from_cart_{video_key}")],
            [InlineKeyboardButton(text="Перейти в корзину", callback_data="show_cart")],
            [InlineKeyboardButton(text="Назад к списку", callback_data="back_to_video_choice")]
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Добавить в корзину", callback_data=f"add_to_cart_{video_key}")],
            [InlineKeyboardButton(text="Перейти в корзину", callback_data="show_cart")],
            [InlineKeyboardButton(text="Назад к списку", callback_data="back_to_video_choice")]
        ])


def get_cart_keyboard(user_id):
    if user_id not in user_carts or not user_carts[user_id]:
        return None

    total_price, final_price, discount = calculate_total_price(user_carts[user_id])

    keyboard = []
    for video_key in user_carts[user_id]:
        video_name = PREVIEWS_INFO[video_key]['name']
        keyboard.append([InlineKeyboardButton(
            text=f"❌ {video_name}",
            callback_data=f"cart_remove_{video_key}"
        )])

    keyboard.extend([
        [InlineKeyboardButton(text="Оформить заказ", callback_data="checkout")],
        [InlineKeyboardButton(text="Очистить корзину", callback_data="clear_cart")],
        [InlineKeyboardButton(text="Продолжить выбор", callback_data="back_to_video_choice"),
         InlineKeyboardButton(text="Главное меню", callback_data="back_to_main")]
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def update_work_message(user_id, chat_id, text, reply_markup=None):
    if user_id in user_work_message:
        try:
            await user_work_message[user_id].edit_text(
                text,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
            return user_work_message[user_id]
        except Exception as e:
            print(f"Ошибка редактирования: {e}")

    sent = await bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="HTML",
        reply_markup=reply_markup
    )
    user_work_message[user_id] = sent
    return sent


async def send_new_message(user_id, chat_id, text, reply_markup=None):
    try:
        if user_id in user_work_message:
            try:
                await user_work_message[user_id].delete()
            except:
                pass
            del user_work_message[user_id]
    except:
        pass
    
    sent = await bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="HTML",
        reply_markup=reply_markup
    )
    user_work_message[user_id] = sent
    return sent


async def send_main_menu(chat_id, user_id):
    main_text = """Я подготовила для вас 9 онлайн разборов.  
Это 9 разных хореографий с разным настроением, с разной скоростью и с разной подачей.

<blockquote>1. <b>Perhaps</b> — хореография с атмосферой загадки и лёгкой недосказанности. Плавная, тягучая, идеально для проработки линий.</blockquote>

<blockquote>2. <b>Масло</b> — скользящая, вязкая манера. Здесь важна текучесть и мягкость, движения будто растекаются в пространстве.</blockquote>

<blockquote>3. <b>Paper</b> — чёткая, графичная хореография с акцентами. Можно почувствовать хрусткость и лёгкую агрессию в подаче.</blockquote>

<blockquote>4. <b>Snap</b> — резкая, импульсивная связка. Быстрая смена положений, много ударов и изоляций. Энергия на максимум.</blockquote>

<blockquote>5. <b>Цыганка</b> — яркая, темпераментная хореография с фолк-вайбом. Можно прожить драйв, свободу и внутренний огонь.</blockquote>

<blockquote>6. <b>T fest</b> — дерзкая, уверенная подача под мощный бит. Подходит, если хочется почувствовать себя в центре внимания без лишней сладости.</blockquote>

<blockquote>7. <b>Порвано</b> — надломленная, чувственная хореография. Здесь есть надрыв, эмоция и немного хаоса в хорошем смысле.</blockquote>

<blockquote>8. <b>Drake</b> — плавная, напевная манера. Движения под вокал, стелиться по полу и работать с настроением «лёгкой меланхолии».</blockquote>

<blockquote>9. <b>Yasmi</b> — женственная, секси-хореография с восточным оттенком. Та самая, когда можно замедлиться, вытащить мягкость и красоту движения.</blockquote>

 <b>Цены:</b>
• 1 видео — 1390₽
• 2 видео — 1790₽
• 3 видео — 2190₽
• 4 видео — 2590₽
• 5 видео — 2990₽
• 6 видео — 3390₽
• 7 видео — 3790₽
• 8 видео — 4190₽
• 9 видео — 4590₽

Выберите видео и добавляйте в корзину!"""

    await send_new_message(user_id, chat_id, main_text, get_main_menu_keyboard(user_id))


@dp.message(Command("start"))
async def start_command(message: types.Message):
    user_id = message.from_user.id

    # Очищаем предыдущее сообщение если есть
    if user_id in user_work_message:
        try:
            await user_work_message[user_id].delete()
            del user_work_message[user_id]
        except:
            pass

    args = message.text.split()
    referer_id = None
    if len(args) > 1:
        try:
            referer_id = int(args[1])
            if referer_id != user_id:
                print(f"Пользователь {user_id} пришел по реферальной ссылке от {referer_id}")
                await bot.send_message(
                    referer_id,
                    f"🎉 Поздравляем! По вашей ссылке пришел новый пользователь @{message.from_user.username or message.from_user.full_name}!"
                )
        except ValueError:
            pass

    video_note_path = "videos/preview.mp4"

    try:
        if os.path.exists(video_note_path):
            video_note_file = FSInputFile(video_note_path)
            await message.answer_video_note(
                video_note=video_note_file,
                duration=15,
                length=320
            )
        else:
            print(f"Файл не найден: {video_note_path}")
    except Exception as e:
        print(f"Ошибка отправки видео: {e}")

    await asyncio.sleep(0.5)

    pognali_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ПОГНАЛИ", callback_data="go_choose_video")]
    ])

    sent = await message.answer(
        "If you need the English version of the bot, follow the link @reji_pantera_bot\n\n"
        "Если хотите остаться в русской версии бота, нажмите «Погнали», чтобы перейти к выбору хореографии",
        parse_mode="HTML",
        reply_markup=pognali_keyboard
    )

    user_work_message[user_id] = sent


@dp.callback_query(lambda c: c.data == "go_choose_video")
async def handle_go(callback: CallbackQuery):
    await callback.answer()

    if callback.from_user.id in user_work_message:
        try:
            await user_work_message[callback.from_user.id].delete()
            del user_work_message[callback.from_user.id]
        except:
            pass

    await send_main_menu(callback.message.chat.id, callback.from_user.id)


@dp.callback_query(lambda c: c.data == "choose_video")
async def handle_choose_video(callback: CallbackQuery):
    await callback.answer()
    choose_text = "👇 <b>Выберите хореографию:</b>\n\n<i>Нажмите на видео, чтобы посмотреть отрывок</i>"
    await update_work_message(
        callback.from_user.id,
        callback.message.chat.id,
        choose_text,
        get_video_choice_keyboard()
    )


@dp.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.answer()
    await send_main_menu(callback.message.chat.id, callback.from_user.id)


@dp.callback_query(lambda c: c.data == "back_to_video_choice")
async def back_to_video_choice(callback: CallbackQuery):
    await callback.answer()
    choose_text = "👇 <b>Выберите хореографию:</b>\n\n<i>Нажмите на видео, чтобы посмотреть отрывок</i>"

    if callback.from_user.id in user_work_message:
        try:
            await user_work_message[callback.from_user.id].delete()
        except:
            pass

    await update_work_message(
        callback.from_user.id,
        callback.message.chat.id,
        choose_text,
        get_video_choice_keyboard()
    )


@dp.callback_query(lambda c: c.data == "add_all_to_cart")
async def add_all_to_cart(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id

    all_videos = [f"video_{i}" for i in range(1, 10)]

    if user_id not in user_carts:
        user_carts[user_id] = []

    user_carts[user_id] = all_videos.copy()

    await callback.answer("✅ Все 9 видео добавлены в корзину!", show_alert=True)

    await show_cart(callback)


@dp.callback_query(lambda c: c.data.startswith("view_video_"))
async def view_video(callback: CallbackQuery):
    await callback.answer()

    video_num = callback.data.split("_")[-1]
    video_key = f"video_{video_num}"
    video_info = PREVIEWS_INFO[video_key]
    preview_path = video_info["preview"]

    in_cart = callback.from_user.id in user_carts and video_key in user_carts[callback.from_user.id]
    cart_status = "✅ В корзине" if in_cart else "❌ Не в корзине"

    caption = f""" <b>{video_info['name']}</b>

{video_info['description']}

Цена: {SINGLE_VIDEO_PRICE} рублей (при покупке одного)
Статус: {cart_status}

<b>Комбо-цены:</b>
• 2 видео — 1790₽
• 3 видео — 2190₽
• 4 видео — 2590₽
• 5 видео — 2990₽
• 6 видео — 3390₽
• 7 видео — 3790₽
• 8 видео — 4190₽
• 9 видео — 4590₽

Добавьте видео в корзину, чтобы продолжить выбор или оформить заказ."""

    if callback.from_user.id in user_work_message:
        try:
            await user_work_message[callback.from_user.id].delete()
        except:
            pass

    if os.path.exists(preview_path):
        video_file = FSInputFile(preview_path)
        sent = await callback.message.answer_video(
            video=video_file,
            caption=caption,
            parse_mode="HTML",
            reply_markup=get_video_view_keyboard(video_key, callback.from_user.id),
            width=1080,
            height=1920,
            supports_streaming=True
        )
        user_work_message[callback.from_user.id] = sent
    else:
        sent = await callback.message.answer(
            caption,
            parse_mode="HTML",
            reply_markup=get_video_view_keyboard(video_key, callback.from_user.id)
        )
        user_work_message[callback.from_user.id] = sent


@dp.callback_query(lambda c: c.data.startswith("add_to_cart_"))
async def add_to_cart(callback: CallbackQuery):
    video_key = callback.data.replace("add_to_cart_", "")
    user_id = callback.from_user.id

    current_count = len(user_carts.get(user_id, []))
    if current_count >= 9:
        await callback.answer("⚠️ Нельзя добавить больше 9 видео!", show_alert=True)
        return

    if user_id not in user_carts:
        user_carts[user_id] = []

    if video_key not in user_carts[user_id]:
        user_carts[user_id].append(video_key)
        await callback.answer(f"✅ {PREVIEWS_INFO[video_key]['name']} добавлен в корзину!", show_alert=True)

        choose_text = "👇 <b>Выберите хореографию:</b>\n\n<i>Нажмите на видео, чтобы посмотреть отрывок</i>"

        if user_id in user_work_message:
            try:
                await user_work_message[user_id].delete()
            except:
                pass

        await update_work_message(
            user_id,
            callback.message.chat.id,
            choose_text,
            get_video_choice_keyboard()
        )


@dp.callback_query(lambda c: c.data.startswith("remove_from_cart_"))
async def remove_from_cart(callback: CallbackQuery):
    video_key = callback.data.replace("remove_from_cart_", "")
    user_id = callback.from_user.id

    if user_id in user_carts and video_key in user_carts[user_id]:
        user_carts[user_id].remove(video_key)
        await callback.answer(f"❌ {PREVIEWS_INFO[video_key]['name']} удален из корзины!", show_alert=True)

        choose_text = "👇 <b>Выберите хореографию:</b>\n\n<i>Нажмите на видео, чтобы посмотреть отрывок</i>"

        if user_id in user_work_message:
            try:
                await user_work_message[user_id].delete()
            except:
                pass

        await update_work_message(
            user_id,
            callback.message.chat.id,
            choose_text,
            get_video_choice_keyboard()
        )


@dp.callback_query(lambda c: c.data.startswith("cart_remove_"))
async def cart_remove_item(callback: CallbackQuery):
    video_key = callback.data.replace("cart_remove_", "")
    user_id = callback.from_user.id

    if user_id in user_carts and video_key in user_carts[user_id]:
        user_carts[user_id].remove(video_key)
        await callback.answer(f"❌ {PREVIEWS_INFO[video_key]['name']} удален из корзины!", show_alert=True)
        await show_cart(callback)


@dp.callback_query(lambda c: c.data == "show_cart")
async def show_cart(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id

    if user_id not in user_carts or not user_carts[user_id]:
        empty_cart_text = "🛒 <b>Ваша корзина пока пуста!</b>\n\nДобавьте видео через раздел «Выбрать видео»."

        if user_id in user_work_message:
            try:
                await user_work_message[user_id].delete()
            except:
                pass

        sent = await callback.message.answer(empty_cart_text, parse_mode="HTML", reply_markup=get_empty_cart_keyboard())
        user_work_message[user_id] = sent
        return

    total_price, final_price, discount = calculate_total_price(user_carts[user_id])
    video_count = len(user_carts[user_id])

    cart_text = f"🛒 <b>ВАША КОРЗИНА</b>\n\n"
    for video_key in user_carts[user_id]:
        video_name = PREVIEWS_INFO[video_key]['name']
        cart_text += f"• {video_name}\n"

    cart_text += f"Выбрано видео: {video_count} шт.\n"
    cart_text += f"<b>К оплате: {final_price}₽</b>"

    if user_id in user_work_message:
        try:
            await user_work_message[user_id].delete()
        except:
            pass

    sent = await callback.message.answer(cart_text, parse_mode="HTML", reply_markup=get_cart_keyboard(user_id))
    user_work_message[user_id] = sent


@dp.callback_query(lambda c: c.data == "clear_cart")
async def clear_cart(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id

    if user_id in user_carts:
        user_carts[user_id] = []

    empty_cart_text = "🛒 <b>Корзина очищена!</b>\n\nДобавьте видео через раздел «Выбрать видео»."

    if user_id in user_work_message:
        try:
            await user_work_message[user_id].delete()
        except:
            pass

    sent = await callback.message.answer(empty_cart_text, parse_mode="HTML", reply_markup=get_empty_cart_keyboard())
    user_work_message[user_id] = sent


@dp.callback_query(lambda c: c.data == "checkout")
async def checkout(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id

    if user_id not in user_carts or not user_carts[user_id]:
        empty_cart_text = "🛒 <b>Ваша корзина пуста!</b>\n\nДобавьте видео через раздел «Выбрать видео»."

        if user_id in user_work_message:
            try:
                await user_work_message[user_id].delete()
            except:
                pass

        sent = await callback.message.answer(empty_cart_text, parse_mode="HTML", reply_markup=get_empty_cart_keyboard())
        user_work_message[user_id] = sent
        return

    total_price, final_price, discount = calculate_total_price(user_carts[user_id])
    video_count = len(user_carts[user_id])

    await state.update_data(
        selected_videos=user_carts[user_id].copy(),
        total_price=final_price,
        video_count=video_count
    )

    payment_id = f"PAY_{user_id}_{int(time.time())}"
    await state.update_data(payment_id=payment_id)

    videos_list = "\n".join([f"• {PREVIEWS_INFO[v]['name']}" for v in user_carts[user_id]])

    payment_details = f"""
💳 <b>ОФОРМЛЕНИЕ ЗАКАЗА</b>

📹 <b>Выбранные видео:</b>
{videos_list}

💰 <b>Стоимость:</b>
Количество видео: {video_count} шт.
Итого к оплате: <b>{final_price}₽</b>

🏦 <b>РЕКВИЗИТЫ ДЛЯ ОПЛАТЫ:</b>
• Карта Сбербанк: 1234 5678 9012 3456
• СБП (по номеру телефона): +7 (999) 123-45-67

🔴🔴🔴 <b>ВНИМАНИЕ! ОБЯЗАТЕЛЬНО ПРОВЕРЬТЕ!</b> 🔴🔴🔴

При оформлении перевода на экране будет показано имя получателя.
✅ <b>Правильное имя: РЕГИНА [Ваша фамилия]</b>

❌ <b>Если видите другое имя - НЕ ПЕРЕВОДИТЕ!</b>
Это могут быть мошенники. Сразу напишите @reji_pantera

🔑 Ваш ID платежа: <code>{payment_id}</code>

📝 <b>ИНСТРУКЦИЯ:</b>
1. Переведите точную сумму {final_price}₽
2. <b>ПРОВЕРЬТЕ имя получателя (должно быть РЕГИНА)</b>
3. В комментарии к переводу укажите ID платежа: <code>{payment_id}</code>
4. Нажмите "✅ Я ОПЛАТИЛ(А)" ниже

⚠️ После подтверждения оплаты вы получите все выбранные видео в течение 1 часа!
"""

    payment_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я ОПЛАТИЛ(А)", callback_data="confirm_payment")],
        [InlineKeyboardButton(text="◀️ Назад в корзину", callback_data="show_cart")],
        [InlineKeyboardButton(text="❓ Помощь", url="https://t.me/reji_pantera")]
    ])

    if user_id in user_work_message:
        try:
            await user_work_message[user_id].delete()
        except:
            pass

    sent = await callback.message.answer(payment_details, parse_mode="HTML", reply_markup=payment_keyboard)
    user_work_message[user_id] = sent
    await state.set_state(PaymentStates.waiting_for_payment)


@dp.callback_query(lambda c: c.data == "confirm_payment")
async def confirm_payment(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    state_data = await state.get_data()
    selected_videos = state_data.get("selected_videos", [])
    total_price = state_data.get("total_price", 0)
    payment_id = state_data.get("payment_id", "unknown")

    videos_names = "\n".join([f"📹 {PREVIEWS_INFO[v]['name']}" for v in selected_videos])

    phone_text = f"""
📱 <b>Пожалуйста, укажите ваш номер телефона</b>

Ваш заказ:
{videos_names}

💰 Сумма: {total_price}₽
🔑 ID платежа: {payment_id}

Для подтверждения оплаты и связи с вами, отправьте номер в формате:

<code>+7XXXXXXXXXX</code>

Пример: <code>+79123456789</code>
"""

    phone_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="show_cart")],
        [InlineKeyboardButton(text="Помощь", url="https://t.me/reji_pantera")]
    ])

    await callback.message.answer(phone_text, parse_mode="HTML", reply_markup=phone_keyboard)
    await state.set_state(PaymentStates.waiting_for_phone)


@dp.message(PaymentStates.waiting_for_phone)
async def handle_phone_input(message: types.Message, state: FSMContext):
    phone = message.text.strip()

    if not phone.startswith('+') or len(phone) < 11:
        await message.answer("❌ Неверный формат! Отправьте номер в формате: +7XXXXXXXXXX")
        return

    state_data = await state.get_data()
    selected_videos = state_data.get("selected_videos", [])
    total_price = state_data.get("total_price", 0)
    payment_id = state_data.get("payment_id", "unknown")

    videos_list = "\n".join([f"• {PREVIEWS_INFO[v]['name']}" for v in selected_videos])
    username_display = f"@{message.from_user.username}" if message.from_user.username else "нет"

    admin_notification = f"""
🔔 <b>НОВЫЙ ЗАКАЗ!</b>

👤 Пользователь: {message.from_user.full_name}
🆔 ID: {message.from_user.id}
📱 Телефон: {phone}
👨‍💻 Username: {username_display}

📹 <b>Заказанные видео:</b>
{videos_list}

💰 <b>Сумма:</b> {total_price}₽
🔑 ID платежа: {payment_id}

❗️ Проверьте оплату и отправьте видео пользователю!
"""

    await bot.send_message(ADMIN_ID, admin_notification, parse_mode="HTML")

    user_id = message.from_user.id
    if user_id in user_carts:
        user_carts[user_id] = []

    await message.answer(
        "✅ <b>ЗАЯВКА ОТПРАВЛЕНА!</b>\n\n"
        f"📹 Вы заказали {len(selected_videos)} видео\n"
        f"💰 Сумма: {total_price}₽\n\n"
        "⏳ <b>Что дальше?</b>\n"
        "1. Администратор проверит оплату\n"
        "2. После проверки вы получите полные видео\n"
        "3. Обычно это занимает до 1 часа\n\n"
        "🙏 Спасибо за доверие!",
        parse_mode="HTML"
    )

    await state.clear()


@dp.message(Command("help"))
async def send_help(message: types.Message):
    help_text = """
🤖 ПОМОЩЬ ПО БОТУ

📹 Как купить онлайн-разбор:
1. Напишите /start
2. Посмотрите видео-презентацию
3. Нажмите "Погнали"
4. Нажмите "Выбрать видео"
5. Выберите видео - посмотрите отрывок
6. Добавьте видео в корзину (➕) или нажмите "⭐️ Хочу всё"
7. Продолжите выбор или перейдите в корзину
8. В корзине оформите заказ
9. Нажмите "✅ Я оплатил(а)"
10. Укажите номер телефона

💰 <b>Цены:</b>
• 1 видео — 1390₽
• 2 видео — 1790₽
• 3 видео — 2190₽
• 4 видео — 2590₽
• 5 видео — 2990₽
• 6 видео — 3390₽
• 7 видео — 3790₽
• 8 видео — 4190₽
• 9 видео — 4590₽
"""
    await message.answer(help_text, parse_mode="HTML")


async def main():
    os.makedirs("videos", exist_ok=True)
    os.makedirs("images", exist_ok=True)

    print("🤖 Бот запущен!")
    print(f"👑 Админ ID: {ADMIN_ID}")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
