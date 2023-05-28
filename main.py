import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
import botkeyboards as bk

# Logging
logging.basicConfig(level=logging.INFO)

# Init the bot
token = os.environ['BOT_KEY']
bot = Bot(token=token)
storage = MemoryStorage()  # Memory for FSM
dp = Dispatcher(bot, storage=storage)


def get_blacklist():
    """Gets black list from the blacklist.csv"""
    with open('blacklist.txt', 'r') as file:
        return [int(line.strip()) for line in file]


def update_blacklist(data: list):
    """Writes the updated black list to the blacklist.csv"""
    with open('blacklist.txt', 'w') as file:
        for item in data:
            file.write(str(item) + '\n')


# Init the DB
blacklist = get_blacklist()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """This handler will be called when user sends `/start` command"""
    if message.chat.type != "private":  # Command has been sent into the group chat. Nothing to do
        return
    await message.reply(
        "<b>Привет, я бот-модератор</b>"
        "\nМоя задача - следить за тем, чтобы в Вашем чате не появлялись пользователи из бан-листа"
        "\n👤 Чтобы добавить(убрать) пользователя в(из) черного списка пришлите его контакт"
        "\n👥️ Черный список  - Просмотреть ЧС",
        parse_mode="HTML",
        reply_markup=bk.rk_main
    )


@dp.message_handler(commands=['help'])
@dp.message_handler(Text(equals="❓ Как прислать контакт?"))
async def send_help(message: types.Message):
    """This handler will be called when user sends `/help` command"""
    if message.chat.type != "private":  # DM only
        return

    caption = (
        "Для добавления или удаления пользователя из черного списка нужно `поделиться контактом`"
        "\nДля этого:"
        "\n1. Зайдите в профиль пользователя (например, через диалог с ним) и откройте меню действий через три точки"
        "\n2. Нажмите `Поделиться контактом`, откроется список диалогов"
        "\n3. Выберите диалог с ботом и нажмите отправить"
        "\n<b>Готово!</b> пользователь добавлен или удален из черного списка"
    )

    images = ["help1.jpg", "help2.jpg", "help3.jpg"]
    media_group = []
    for path in images:
        photo_file = types.InputFile(path)
        media_group.append(types.InputMediaPhoto(photo_file))

    await message.reply(caption, parse_mode="HTML")
    await message.answer_media_group(media=media_group)


@dp.message_handler(content_types=["contact"])
async def toggle_ban_contact(message: types.Message):
    """This handler will be called if the message content type is `contact`"""

    if message.chat.type != "private":  # DM only
        return

    contact = message.contact
    user_id = contact.user_id
    user_link = f"<a href='tg://user?id={user_id}'>Ссылка</a>"

    if user_id in blacklist:
        switch_text = "удалён из чёрного списка"
        blacklist.remove(user_id)
    else:
        switch_text = "добавлен в чёрный список"
        blacklist.append(user_id)

    await message.reply(f"Пользователь ({user_link}) был {switch_text}", parse_mode="HTML")

    update_blacklist(blacklist)


@dp.message_handler(commands=['get_list'])
@dp.message_handler(Text(equals="👥️ Черный список"))
async def send_blacklist(message: types.Message):
    """This handler will be called when user sends `/get_list` command"""
    if message.chat.type != "private":  # DM only
        return

    if not blacklist:
        await message.reply("В чёрном списке ещё никого нет!")
        return

    text = "Чёрный список:"
    for i, user_id in enumerate(blacklist):
        text += f"\n<a href='tg://user?id={user_id}'>Пользователь {i + 1}</a>"

    await message.reply(text, parse_mode="HTML")


@dp.message_handler(content_types=["new_chat_members"])
async def on_user_join(message: types.Message):
    """This handler will be called when anyone joins the chat"""
    # Ban if in blacklist
    for user in message.new_chat_members:
        if user.id in blacklist:
            await message.delete()
            await message.chat.kick(user_id=user.id)


@dp.message_handler(content_types=["left_chat_member"])
async def on_user_left(message: types.Message):
    """This handler will be called when anyone lefts the chat. Deletes message if user is banned"""
    if message.left_chat_member.id in blacklist:
        await message.delete()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
