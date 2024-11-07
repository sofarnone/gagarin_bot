import asyncio
import logging
import sys, os
import qrcode
import samples
from datetime import timedelta, datetime as dt


from aiogram import Bot, Dispatcher, html, F, flags
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.chat_action import ChatActionMiddleware
from aiogram.enums import ParseMode
from aiogram.filters import (
    CommandStart,
    Command,
    Command,
    IS_MEMBER,
    IS_NOT_MEMBER,
    IS_ADMIN,
    ChatMemberUpdatedFilter,
)

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
    ReplyKeyboardRemove,
    Message,
    ChatMemberUpdated,
    ContentType,
    WebAppData,
    FSInputFile,
    InlineKeyboardButton,
    CallbackQuery,
)
from aiogram.methods.get_chat_administrators import GetChatAdministrators
import database as db

# from module1 import router  # type: ignore

# СОЗДАНИЕ ТАБЛИЦЫ
db.create()

bot = Bot(token=samples.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.message.middleware(ChatActionMiddleware())

# Кнопка Играть!
button = KeyboardButton(
    text=samples.PLAYBUTTON,
    web_app=WebAppInfo(url=samples.GAMEURL),
)
keyboard = ReplyKeyboardMarkup(
    keyboard=[[button]], resize_keyboard=True, one_time_keyboard=True
)


async def get_chat_admins() -> None:
    admin_list = samples.admin_list
    chat_admins = await bot.get_chat_administrators(samples.GROUP_ID)
    for i in chat_admins:
        admin_list.add(i.user.id)


startphoto = FSInputFile(os.path.dirname(__file__) + "/src/picture.jpg")
helpgif = FSInputFile(os.path.dirname(__file__) + "/src/gameplay.gif")


@dp.message(CommandStart())
@flags.chat_action("typing")
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.set_state()
    sample = samples.INTRODUCTION

    user_channel_status = await bot.get_chat_member(
        chat_id=samples.GROUP_ID, user_id=message.from_user.id
    )
    if user_channel_status.status == "left":
        return await message.answer(
            samples.SUBSCRIBE,
            reply_markup=ReplyKeyboardRemove(),
        )

    user = db.get_user(message.chat.id)
    if not user:
        db.create_user(message.chat.id, message.chat.first_name)
    text = ""
    kb = ReplyKeyboardRemove()
    lastplay = user["lastplay"] if user else None
    if lastplay:
        if dt.fromisoformat(lastplay) + timedelta(hours=24) > dt.now():
            t = dt.fromisoformat(lastplay) + timedelta(hours=24) - dt.now()
            text = (
                sample
                + f"Вы сегодня уже играли в игру! Возвращайтесь через <b>{timedelta(seconds=t.seconds)}</b>."
            )
            kb = ReplyKeyboardRemove()
        else:
            text = sample + "С возвращением!\nЖми «Играть 🔥», и погнали"
            kb = keyboard
    else:
        text = sample + "Готов начать? Просто нажми «Играть 🔥», и мы погнали! 🎮✨"
        kb = keyboard

    await message.answer_photo(
        photo=startphoto,
        caption=text,
        reply_markup=kb,
    )


@dp.message(Command("help"))
@flags.chat_action("typing")
async def command_help_handler(message: Message, state: FSMContext) -> None:
    await state.set_state()
    await message.answer_animation(
        animation=helpgif,
        caption=samples.GAMEPLAY,
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(Command("my_promocode"))
@flags.chat_action("typing")
async def command_clear_handler(message: Message, state: FSMContext) -> None:
    await state.set_state()
    pass


@dp.message(Command("clear"))
@flags.chat_action("typing")
async def command_clear_handler(message: Message, state: FSMContext) -> None:
    await state.set_state()
    if message.chat.id in samples.admin_list:
        db.set_user(message.chat.id, lastplay=None)
        await message.answer(
            f"Время последней игры для {message.chat.first_name} очищено!"
        )


# кнопка подтвердить у админов при проверке промокода
builder = InlineKeyboardBuilder()
builder.add(InlineKeyboardButton(text="Подтвердить", callback_data="check_promo"))


class MyCallback(CallbackData, prefix="my"):
    action: str
    promocode: str
    user_id: int
    edit_mes_id: int
    discount: int


class Form(StatesGroup):
    check = State()


@dp.message(Command("check"))
@flags.chat_action("typing")
async def check_promo(message: Message, state: FSMContext) -> None:
    if message.from_user.id not in samples.admin_list:
        return

    message_list = message.text.split()
    current_state = await state.get_state()
    if current_state is None:
        if len(message_list) <= 1:
            await state.set_state(Form.check)
            return await message.answer("Укажите промокод для проверки")
        elif len(message_list) > 1:
            promo = message_list[1]
    elif current_state == "Form:check":
        promo = message.text
        await state.set_state()

    user_promo = db.get_promocode(promo)
    if not user_promo:
        return await message.reply("Такого промокода нет в базе данных!")

    markup = InlineKeyboardBuilder().add(
        InlineKeyboardButton(
            text=f"Подтвердить",
            callback_data=MyCallback(
                action="check",
                promocode=promo,
                user_id=int(user_promo["tid"]),
                edit_mes_id=int(user_promo["message_id"]),
                discount=int(user_promo["discount"]),
            ).pack(),
        ),
    )
    if dt.fromisoformat(user_promo["till"]) < dt.now():
        db.delete_promocode(promo)
        return await message.answer(
            f"\nПромокод {promo} присутствует в базе данных!\nСумма скидки: {user_promo["discount"]}\n\n<b>Срок действия промокода истек!\nПромокод удален!</b>"
        )
    date, time = dt.fromisoformat(user_promo["till"]).strftime(
        "%d.%m.%y"
    ), dt.fromisoformat(user_promo["till"]).strftime("%H:%M")
    await message.answer(
        f"\nПромокод {promo} присутствует в базе данных!\nСумма скидки: {user_promo["discount"]}\n\nДействует до: {date} {time}",
        reply_markup=markup.as_markup(),
    )


@dp.callback_query(MyCallback.filter(F.action == "check"))
async def check_promo_confirm(query: CallbackQuery, callback_data: MyCallback):
    try:
        nowtime = dt.now()
        await bot.delete_message(
            chat_id=callback_data.user_id, message_id=callback_data.edit_mes_id
        )
        await bot.send_message(
            chat_id=callback_data.user_id,
            text=f"Вы успешно воспользовались промокодом!",
        )
    except Exception as e:
        print(e)

    db.delete_promocode(callback_data.promocode)
    await bot.edit_message_text(
        text=f"Промокод успешно применен!\nСумма скидки: {callback_data.discount}",
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
    )


@dp.message(F.content_type == ContentType.WEB_APP_DATA)
@flags.chat_action("typing")
async def web_app_handler(data: WebAppData):
    score = int(data.web_app_data.data)
    if score > 0:
        if score > 100:
            score = 100

        promocode = samples.get_promo_code(10)  # генерируем промокод

        img = qrcode.make(f"/check {promocode}")
        img.save(f"{promocode}.png")  # ГЕНЕРАТОР КЬАР КОДА
        qrcode_img = FSInputFile(f"{promocode}.png")

        stamp = f"Сумма скидки: {int(score)} р.\nДата получения: {dt.now().strftime('%d.%m.%Y %H:%M')}\nСкидка действует до {(dt.now()+timedelta(hours=24)).strftime('%d.%m.%Y %H:%M')}.\n\nПромокод: {promocode}"
        win_message = await data.answer_photo(
            photo=qrcode_img,
            caption=samples.WINGAME + stamp,
            reply_markup=ReplyKeyboardRemove(),
        )

        os.remove(f"{promocode}.png")
        db.add_promocode(
            promocode=promocode,
            tid=data.chat.id,
            message_id=win_message.message_id,
            till=(dt.now() + timedelta(hours=24)).isoformat(),
            discount=score,
        )
    # ЕСЛИ В ИГРЕ МОЖНО ПРОИГРАТЬ!
    elif score == 0:
        db.set_user(data.chat.id, lastplay=dt.now().isoformat())
        await data.answer(
            samples.LOSEGAME,
            reply_markup=ReplyKeyboardRemove(),
        )


@dp.message()
@flags.chat_action("typing")
async def echo_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == "Form:check":
        return await check_promo(message, state)

    await message.answer(
        samples.DONTUNDERSTAND,
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
@flags.chat_action("typing")
async def chat_member_handler(event: ChatMemberUpdated):
    samples.WELCOME
    try:
        await bot.send_message(
            event.from_user.id, samples.WELCOME, reply_markup=ReplyKeyboardRemove()
        )
    except:
        pass
    db.log(f"user {event.new_chat_member.user.first_name} joined the group")


@dp.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_ADMIN))
async def chat_member_handler(event: ChatMemberUpdated):
    samples.admin_list.add(event.new_chat_member.user.id)
    try:
        await bot.send_message(
            event.new_chat_member.user.id,
            samples.NEW_ADMIN,
        )
    except:
        pass
    db.log(f"user {event.new_chat_member.user.first_name} added to admin list")


@dp.chat_member(ChatMemberUpdatedFilter(IS_ADMIN >> IS_MEMBER))
async def chat_member_handler(event: ChatMemberUpdated):
    if event.new_chat_member.user.id in samples.admin_list:
        samples.admin_list.remove(event.new_chat_member.user.id)
    db.log(f"user {event.new_chat_member.user.first_name} deleted from admin list")


async def main() -> None:
    await get_chat_admins()
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
