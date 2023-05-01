import os

from aiogram import Bot, Dispatcher, executor, types

bot = Bot(token=os.environ["TOKEN"], parse_mode=types.ParseMode.HTML)

dp = Dispatcher(bot)


async def predict(text: str):  # pylint: disable=unused-argument
    import random

    return random.choice(["YES", "NO"])


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "👋 <b>Привет, товарищ!</b> Я найду биржевой сленг в любом предложенном тексте."
        " Чтобы начать, просто отправь его мне 😏"
    )


@dp.message_handler()
async def echo(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    result = await predict(message.text)
    await message.answer(result)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
