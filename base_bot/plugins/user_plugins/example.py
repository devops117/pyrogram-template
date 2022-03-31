from pyrogram import Client, filters
from pyrogram.types import Message


@Client.on_message(filters.command('ping') & filters.user("self"))
async def ping(_, msg: Message):
    await msg.reply_text("PONG")
