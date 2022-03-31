from pyrogram import Client, filters
from pyrogram.types import Message


@Client.on_message(filters.command('ping'))
async def ping(client: Client, msg: Message):
    if not msg.from_user.id in client.wheel_userids:
        return
    await msg.reply_text("PONG")
