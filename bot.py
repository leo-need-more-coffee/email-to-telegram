import datetime
import time
from datetime import date
import sched
import json
import asyncio
from config import *
import logging
import db
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputFile
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
import os

attr_list = (
    "[0] - Delivered-To\n"
    "[1] - Return-path\n"
    "[2] - Received-SPF\n"
    "[3] - Received\n"
    "[4] - DKIM-Signature\n"
    "[9] - MIME-Version\n"
    "[10] - From\n"
    "[11] - Date\n"
    "[12] - Message-ID\n"
    "[13] - Subject\n"
    "[14] - To\n"
    "[15] - Content-Type\n"
)


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    imap = State()
    username = State()
    password = State()
    attr = State()


async def send(id, text):
    await bot.send_message(id, text, parse_mode= 'Markdown')

async def files(id, pathname):
    files = os.listdir('./'+str(pathname))
    uploaded_files = [InputFile('./'+str(pathname)+'/'+el, filename=el) for el in files]
    for el in uploaded_files: await bot.send_document(id, el)
    for el in files: print(el);os.remove('./'+str(pathname)+'/'+el)
    os.rmdir('./'+str(pathname))


@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    await message.reply("хой, это меилбокс, пишите /signup")


@dp.message_handler(commands=['signup'])
async def start(message: types.Message):
    id = message.from_user.id
    chat_id = message.chat.id
    if not await db.is_user(id):
        await db.create_user(id, is_editing=True)
    else:
        user = await db.get_user(id)
        await db.create_user(id, number=len(user), is_editing=True)
    user = await db.get_editing_data(id)
    user["chat_id"] = chat_id
    await db.edit_user(user)
    await message.reply("Укажите ваш imap сервер:")
    await Form.imap.set()


@dp.message_handler(state=Form.imap)
async def set_imap(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if message.text == "/exit":
        await state.finish()
        return
    user = await db.get_editing_data(id)
    user["imap"] = message.text
    await db.edit_user(user)
    await message.answer("Введите username(полную почту):")
    await Form.username.set()


@dp.message_handler(state=Form.username)
async def set_username(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if message.text == "/exit":
        await state.finish()
        return
    user = await db.get_editing_data(id)
    user["username"] = message.text
    await db.edit_user(user)
    await message.answer(
        "Введите password(возможно придется создать пароль для приложений в настройках почтового клиента):")
    await Form.password.set()


@dp.message_handler(state=Form.password)
async def set_username(message: types.Message, state: FSMContext):
    id = message.from_user.id
    if message.text == "/exit":
        await state.finish()
        return
    user = await db.get_editing_data(id)
    user["password"] = message.text
    user["is_editing"] = False
    await db.edit_user(user)
    await message.answer(
        "Регистрация завершена, если вы правильно ввели данные, сюда будут приходить письма. Если какая-то проблема - пишите @pzrnqt1vrss")
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, )
