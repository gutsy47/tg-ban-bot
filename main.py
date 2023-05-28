import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ChatActions

import botkeyboards as bk

# Logging
logging.basicConfig(level=logging.INFO)

# Init the bot
token = os.environ['BOT_KEY']
bot = Bot(token=token)
storage = MemoryStorage()  # Memory for FSM
dp = Dispatcher(bot, storage=storage)


# (un)ban form
class BanForm(StatesGroup):
    username = State()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """This handler will be called when user sends `/start` command"""
    if message.chat.type != "private":  # Command has been sent into the group chat. Nothing to do
        return
    await message.reply(
        "<b>Привет, я бот-модератор</b>"
        "\nМоя задача - следить за тем, чтобы в Вашем чате не появлялись пользователи из бан-листа"
        "\nВот список доступных команд:"
        "\n🔴 Заблокировать  - Добавить пользователя в ЧС"
        "\n🟢 Разблокировать - Удалить пользователя из ЧС"
        "\n👥️ Черный список  - Просмотреть ЧС",
        parse_mode="HTML",
        reply_markup=bk.rk_main
    )


@dp.message_handler(content_types=["new_chat_members"])
async def on_user_join(message: types.Message):
    """This handler will be called when anyone joins the chat"""
    # Ban if in blacklist
    blacklist = [6086502107]
    for user in message.new_chat_members:
        if user.id in blacklist:
            await message.chat.kick(user_id=user.id)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
