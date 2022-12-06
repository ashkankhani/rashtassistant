from config import *
from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Message,InlineKeyboardMarkup,InlineKeyboardButton
import asyncio






api = Client('bot' , api_id=api_id , api_hash=api_hash , bot_token=bot_token)



@api.on_message(filters.group)
async def messageControl(client:Client , message:Message):
    print(message.chat)
    message.continue_propagation()



@api.on_message(filters.group & filters.regex(r'^!rmute$'))
async def raidMute(client:Client , message:Message):
    if(message.sender_chat):
        pass


@api.on_message(filters.group & filters.regex(r'^!rban$'))
async def raidBan(client:Client , message:Message):
    if(message.sender_chat):
        pass


@api.on_message(filters.group & filters.regex(r'^!save$'))
async def savePost(client:Client , message:Message):
    await message.reply(
        text='هروقت ادمین روی دکمه زیر کلیک کرد برات میفرستمش',
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text='اجازه میدم',callback_data=f'save{message.from_user.id}')]
            ]
        ))
















api.run()



