from config import *
from pyrogram import Client
from pyrogram import filters
from pyrogram.types import (Message,InlineKeyboardMarkup,InlineKeyboardButton,
CallbackQuery,InputTextMessageContent,InlineQueryResultCachedDocument)
from pyrogram.errors import UserIsBlocked
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid
import uuid
import mysql.connector
from mysql.connector import errorcode
import asyncio



class Database:
    def __init__(self):
        self.cnx = mysql.connector.connect(**dbconfig)
        self.cursor = self.cnx.cursor()
    def configureTables(self):
        tables = {}
        tables['users'] = (
            "create table if not exists users( "
            "id int not null unique auto_increment,"
            "userid varchar(20) primary key,"
            "nickname varchar(50)"
            ");"
        )
        tables['files'] = (
            "create table if not exists files( "
            "id int not null unique auto_increment, "
            "fileid varchar(100) primary key, "
            "title varchar(100), "
            "filedes varchar(500), "
            "accept int default 0, "
            "senderid varchar(20), "
            "foreign key(senderid) references users(userid) "
            ");"
        )
        for table in tables:
            self.cursor.execute(tables[table])
        self.cnx.commit()
        self.cursor.close()
        self.cnx.close()
    def isUserSaved(self,userid):
        pass
        





api = Client('bot' , api_id=api_id , api_hash=api_hash , bot_token=bot_token)
db = Database()
db.configureTables()
@api.on_callback_query(filters.regex(r'savepost_(\d+)'))
async def savePostCallBack(client:Client , query:CallbackQuery):
    print(query)
    clickerId = query.from_user.id
    chatId = query.message.chat.id
    reciever = query.message.reply_to_message.from_user.id
    messageId = int(query.matches[0].group(1))

    clicker = await client.get_chat_member(chatId,clickerId)
    print(clicker)
    if(clicker.status == ChatMemberStatus.OWNER or clicker.status == ChatMemberStatus.ADMINISTRATOR):
        try:
            await client.copy_message(reciever,chatId,messageId)
        except UserIsBlocked as e:
            await query.message.reply_to_message.reply_text('منو بلاک کردی که!')
        except PeerIdInvalid as e:
            await query.message.reply_to_message.reply_text('اول بیا پی وی منو استارت کن!')
        
        else:
            await query.message.edit('ارسال شد :)')
    else:
        await query.answer('تو ادمین نیستی که!')
    
        

# @api.on_message(filters.group)
# async def messageControl(client:Client , message:Message):
#     print(message.chat)
#     message.continue_propagation()



# @api.on_message(filters.group & filters.regex(r'(?i)^!rmute$'))
# async def raidMute(client:Client , message:Message):
#     if(message.sender_chat):
#         pass


# @api.on_message(filters.group & filters.regex(r'(?i)^!rban$'))
# async def raidBan(client:Client , message:Message):
#     if(message.sender_chat):
#         pass


@api.on_message(filters.group & filters.regex(r'(?i)^!save$') & filters.reply)
async def savePost(client:Client , message:Message):
    await message.reply(
        text='هروقت ادمین روی دکمه زیر کلیک کرد برات میفرستمش',
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text='اجازه میدم',callback_data=f'savepost_{message.reply_to_message_id}')]
            ]
        ))


@api.on_message(filters.private & ~filters.chat(owner_id))
async def userChecker(client:Client,message:Message):
    message.reply('hello')


@api.on_inline_query()
async def answer(client, inline_query):
    await inline_query.answer(
        results=[
            InlineQueryResultCachedDocument(
                id= str(uuid.uuid4()),
                document_file_id='BQACAgQAAxkDAAITqGOZ8EdKtWQR8sngc55rcYOvzINjAAIyDAACk87BUNu7CUHKspEXHgQ',
                title="title",
                description="des",
            ),
        ],
        cache_time=1
    )











api.run()



