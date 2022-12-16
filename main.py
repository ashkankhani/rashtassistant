from config import *
from pyrogram import Client
from pyrogram import filters
from pyrogram.types import (Message,InlineKeyboardMarkup,InlineKeyboardButton,
CallbackQuery,InputTextMessageContent,InlineQueryResultCachedDocument,ReplyKeyboardMarkup,KeyboardButton,InlineQuery)
from pyrogram.errors import UserIsBlocked
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid
import uuid
import mysql.connector
from mysql.connector import errorcode
import asyncio
from mysql.connector.cursor import MySQLCursor
from mysql.connector.connection import MySQLConnection
from enum import Enum,auto


class UserState(Enum):
    NICKNAME = auto()
    DOCUMENT = auto()
    TITLE = auto()
    DESCRIPTION = auto()
class Database:
    def __init__(self)->None:
        self.cnx:MySQLConnection = mysql.connector.connect(**dbconfig)
        self.cursor:MySQLCursor = self.cnx.cursor()

    def __del__(self)->None:
        self.cursor.close()
        self.cnx.close()

    def configureTables(self)->None:
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
            "id int primary key auto_increment, "
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
    

    def getUserData(self,userid)->tuple:
        sql = (
            "select * from users "
            "where userid = %s"
        )
        self.cursor.execute(sql,(userid,))
        return self.cursor.fetchone()
    def saveUserID(self,userid) -> None:
        sql = (
            "insert into users "
            "(userid) "
            "values(%s)"
        )
        self.cursor.execute(sql,(userid,))
        self.cnx.commit()

    def saveUserNickName(self,nickname,userid) -> None:
        sql = (
            "update users "
            "set nickname = %s "
            "where userid = %s"
        )
        self.cursor.execute(sql,(nickname,userid,))
        self.cnx.commit()
    
    def saveDocumentFileId(self,fileid,userid):
        sql = (
            "insert into files "
            "(fileid,senderid) "
            "values(%s,%s)"
        )
        self.cursor.execute(sql,(fileid,userid))
        self.cnx.commit()
    
    def updateDocumentTitle(self,title,userid):
        sql = (
            "update files "
            "set title = %s "
            "where senderid = %s "
            "order by id desc "
            "limit 1"
        )
        self.cursor.execute(sql,(title,userid))
        self.cnx.commit()
    
    def updateDocumentDes(self,filedes,userid):
        sql = (
            "update files "
            "set filedes = %s "
            "where senderid = %s "
            "order by id desc "
            "limit 1"
        )
        self.cursor.execute(sql,(filedes,userid))
        self.cnx.commit()
    
    def getUserLastDocumentData(self,userid):
        sql = (
            "select files.*,users.nickname "
            "from files "
            "inner join users "
            "on files.senderid = users.userid "
            "where senderid = %s "
            "order by files.id desc "
            "limit 1"
        )
        self.cursor.execute(sql,(userid,))
        return self.cursor.fetchone()
    def acceptFile(self,id):
        sql = (
            "update files "
            "set accept = 1 "
            "where id = %s"
        )
        self.cursor.execute(sql,(id,))
        self.cnx.commit()
    def rejectFile(self,id):
        sql = (
            "delete files "
            "where id = %s"
        )
        self.cursor.execute(sql,(id,))
        self.cnx.commit()

    def getAcceptedFiles(self,word)->list:
        sql = (
            'select * from files '
            'where accept = 1 and title like %s'
        )
        self.cursor.execute(sql,('%'+word+'%',))
        return self.cursor.fetchall()
        
        

        







api = Client('bot' , api_id=api_id , api_hash=api_hash , bot_token=bot_token,proxy={
    'scheme' : 'socks5',
    'hostname' : '127.0.0.1',
    'port': 9150
})
db = Database()
db.configureTables()
del db
userStates = {}


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


@api.on_callback_query(filters.regex(r'accept_(\d+)_(\d+)'))
async def acceptFile(client:Client , query:CallbackQuery):
    id = query.matches[0].group(1)
    userid = int(query.matches[0].group(2))
    db = Database()
    db.acceptFile(id)
    await query.answer('جزوه تایید شد')
    await query.edit_message_caption('جزوه تایید شد')
    await client.send_message(userid,f'جزوه شما با آیدی {id} مورد تایید قرار گرفت!')
    

@api.on_callback_query(filters.regex(r'reject_(\d+)_(\d+)'))
async def rejectFile(client:Client , query:CallbackQuery):
    id = query.matches[0].group(1)
    userid = int(query.matches[0].group(2))
    db = Database()
    db.rejectFile(id)
    await query.answer('جزوه رد شد')
    await query.edit_message_caption('جزوه رد شد')
    await client.send_message(userid,f'جزوه شما با آیدی {id} مورد تایید قرار نگرفت!')
    
        

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

@api.on_message(filters.private & (filters.regex(r'^بازگشت به صفحه اصلی$') or filters.command('start')))
async def returnHome(client:Client , message:Message):
    try:
        del userStates[message.chat.id]
    except:
        pass
    message.continue_propagation()

@api.on_message(filters.private & ~filters.chat(owner_id))
async def userChecker(client:Client,message:Message):
    db = Database()
    text = (
            'برای کار با ربات,لطفا یک لقب برای خود انتخاب کنید\n'
            'این لقب برای قسمت ارسال جزوه استفاده خواهد شد'
    )
    userState = userStates.get(message.chat.id)
    try:
        db.saveUserID(message.chat.id)
    except mysql.connector.IntegrityError as err:
        #exists
        userData = db.getUserData(message.chat.id)
        if(userData[2] is None and userState is None):
            await message.reply(text)
            userStates[message.chat.id]=UserState.NICKNAME
            return

        message.continue_propagation()

    else:
        #it's a new user
        await message.reply(text)
        userStates[message.chat.id]=UserState.NICKNAME


    

@api.on_message(filters.private & filters.regex(r'^ارسال جزوه$'))
async def sendDocument(client:Client , message:Message):
    replyMarkup = ReplyKeyboardMarkup(
        [
            ['بازگشت به صفحه اصلی']
        ],resize_keyboard=True
    )
    await message.reply('لطفا فایل جزوه را ارسال کنید...',reply_markup=replyMarkup)
    userStates[message.chat.id] = UserState.DOCUMENT

@api.on_message(filters.private & filters.text)
async def inputText(client:Client , message:Message):
    replyMarkup = ReplyKeyboardMarkup(
        [
            ['بازگشت به صفحه اصلی']
        ],resize_keyboard=True
    )
    if(message.chat.id == owner_id):
        return
    db = Database()
    userState = userStates.get(message.chat.id)
    if(userState is None):
        replyMarkup = ReplyKeyboardMarkup(
            [
                [KeyboardButton('ارسال جزوه')]
            ],resize_keyboard=True
        )
        await message.reply(
            (
                'به صفحه اصلی خوش آمدید!\n'
                'لطفا یک گزینه انتخاب کنید:'
            ),reply_markup=replyMarkup
        )
        return

    if(userState == UserState.NICKNAME):
        db.saveUserNickName(message.text , message.chat.id)
        await message.reply('لقب با موفقیت ذخیره شد!')
        del userStates[message.chat.id]
        return

    if(userState == UserState.TITLE):
        db.updateDocumentTitle(message.text , message.chat.id)
        await message.reply(
            (
                'عنوان جزوه ذخیره شد\n'
                'لطفا توضیحات جزوه را ارسال کنید:'
            ),reply_markup=replyMarkup
        )
        userStates[message.chat.id] = UserState.DESCRIPTION
        return

    if(userState == UserState.DESCRIPTION):
        db.updateDocumentDes(message.text , message.chat.id)
        data = db.getUserLastDocumentData(message.chat.id)
        replyMarkup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('✅',callback_data=f'accept_{data[0]}_{message.chat.id}'),InlineKeyboardButton('❌',callback_data=f'reject_{data[0]}_{message.chat.id}')]
            ]
        )
        await message.reply(
            (
                'توضیحات جزوه ذخیره شد\n'
                'اطلاعات مربوطه به ادمین ربات ارسال شده و بعد از تایید,برای کاربران قابل دسترسی است\n'
                f'آیدی جهت پیگیری: {data[0]}'
            )
        )
        await client.send_document(owner_id,caption=(
            f'عنوان:{data[2]}\n'
            f'توضیحات:{data[3]}\n'
            f'آیدی کاربر:{data[5]}\n'
            f'لقب کاربر:{data[6]}'
        ),document=data[1],reply_markup=replyMarkup)
        del userStates[message.chat.id]
        return
    message.continue_propagation()

@api.on_message(filters.private & ~filters.chat(owner_id) & filters.document)
async def inputDocument(client:Client,message:Message):
    userState = userStates.get(message.chat.id)
    if(userState is None):
        replyMarkup = ReplyKeyboardMarkup(
            [
                [KeyboardButton('ارسال جزوه')]
            ],resize_keyboard=True
        )
        await message.reply(
            (
                'به صفحه اصلی خوش آمدید!\n'
                'لطفا یک گزینه انتخاب کنید:'
            ),reply_markup=replyMarkup
        )
        return
    if(userState == UserState.DOCUMENT):
        db = Database()
        db.saveDocumentFileId(message.document.file_id,message.chat.id)
        userStates[message.chat.id] = UserState.TITLE
        replyMarkup = ReplyKeyboardMarkup(
        [
            ['بازگشت به صفحه اصلی']
        ],resize_keyboard=True
        )
        await message.reply(
            (
                'جزوه ذخیره شد!\n'
                'لطفا عنوان جزوه را ارسال نمایید:'
            )
        )
        return
    
    message.continue_propagation()


@api.on_message(filters.private & ~filters.chat(owner_id))
async def junkMessage(client:Client,message:Message):
    await message.reply(
        (
            'متوجه نشدم چی گفتی\n'
            'با دستور /start میتونی به صفحه اصلی برگردی!'
        )
    )


@api.on_inline_query()
async def answer(client, inline_query:InlineQuery):
    
    results = []
    db = Database()
    for tup in db.getAcceptedFiles(inline_query.query):
        results.append(
            InlineQueryResultCachedDocument(
                document_file_id=tup[1],
                title=tup[2],
                description=tup[3],
            )
        )
    await inline_query.answer(
        results,cache_time=1
    )



api.run()



