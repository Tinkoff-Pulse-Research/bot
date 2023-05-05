import os
import re

from aiohttp import ClientSession
from aiogram import Bot, Dispatcher, executor, types
from typing import Optional
import logging

os.environ['TOKEN'] = "6073666087:AAG5Tkyebp886eBmyj-c83FLyftGFVBJJes"
os.environ['API_URL'] = 'http://127.0.0.1:3000'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.environ["TOKEN"], parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


def remove_punctuation(s: str) -> str:
    """Removes all punctuation in text excluding dashes and hyphens"""
    for sign in ",.!?<>@#$%^&*()_+=:;'\"/\\":
        s = s.replace(sign, "")
    return s


async def predict(text: str) -> Optional[dict]:
    async with ClientSession() as session:
        async with session.post(
                f"{os.environ['API_URL']}/detect_slang",
                json={
                    "text": text
                }
        ) as res:
            if res.status != 200:
                logging.error(f"Got API error while detecting slang. ({await res.text()})")
                return None
            data = await res.json()
    return data


async def get_term_definition(term: str) -> Optional[tuple[str, str]]:
    async with ClientSession() as session:
        async with session.get(f"{os.environ['API_URL']}/term/{term}") as res:
            if res.status not in {404, 200}:
                logging.error(f"Got API error while getting term definition. ({await res.text()})")
                return None
            data = await res.json()
            print(data)
            return (data['result']['definition'], data['result']['key'])\
                if data['status'] == 'ok' else ("", "")


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "👋 <b>Привет, товарищ!</b> Я найду биржевой сленг в любом предложенном тексте."
        " Чтобы начать, просто отправь его мне 😏"
    )


@dp.message_handler()
async def echo(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    text = re.split(r"\s", message.text.strip())
    definition, key = await get_term_definition(remove_punctuation(message.text.strip()))
    logging.info(f"Definition: {definition}")
    if definition:
        return (
            await message.answer(f"<b>{key}</b> – {definition}")
            if definition
            else await message.answer("<b>😢 Определение не найдено</b>")
        )
    result = await predict(message.text)
    logging.info(result)
    if not result['result']['slang']:
        return await message.answer("<b>🙃 Сленг не найден</b>")
    for item in result['result']['highlight']:
        ind, method = item.split("_")
        if ":" in ind:
            s_ind, f_ind = map(int, ind.split(":"))
            print(text[s_ind:f_ind + 1], result['result']['highlight'][item])
            text[s_ind] = f"<code><b>{text[s_ind]}"
            text[f_ind] = f"{text[f_ind]}</b></code>"
        else:
            ind = int(ind)
            print(text[ind], result['result']['highlight'][item])
            if method == 'ml':
                text[ind] = f"<b><u>{text[ind]}</u></b>"
            elif method == 'determined':
                text[ind] = f"<code><b>{text[ind]}</b></code>"
    await message.answer(" ".join(text))


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
