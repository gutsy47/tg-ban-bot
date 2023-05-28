from aiogram.types import reply_keyboard as rk

rk_main = rk.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
rk_main.add(
    rk.KeyboardButton("🔴 Заблокировать"),
    rk.KeyboardButton("🟢 Разблокировать"),
    rk.KeyboardButton("👥️ Черный список")
)

