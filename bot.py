#!/usr/bin/env python3

import os
import logging
from datetime import datetime

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
ApplicationBuilder,
CommandHandler,
MessageHandler,
ConversationHandler,
ContextTypes,
filters
)
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = -1003518003389
ADMIN_ID = 8509876738  # PUT YOUR TELEGRAM ID

LANG, NAME, PHONE, COURSE, CLASS, TIME, LOCATION = range(7)

logging.basicConfig(level=logging.INFO)

registered_users = set()

language_map = {
"English":"en",
"አማርኛ":"am",
"Afaan Oromoo":"om"
}

courses = {

"en":[
["Mobile Maintenance"],
["Advanced Mobile Software"],
["Advanced Mobile Hardware"],
["Laptop & Computer Maintenance"],
["Basic Computer"],
["TV,Decoder & Geepas Maintenance"]
],

"am":[
["ሞባይል ጥገና"],
["አድቫንስድ የሞባይል ሶፍትዌር"],
["አድቫንስድ የሞባይል ሀርድዌር"],
["ላፕቶፕ እና ኮምፒውተር ጥገና"],
["መሰረታዊ ኮምፒውተር"],
["የቲቪ፣ዲኮደር እና ጂፓስ ጥገና"]
],

"om":[
["Suphaa Mobaayilaa"],
["Mobile Software Olaanaa"],
["Mobile Hardware Olaanaa"],
["Suphaa Laptop & Computer"],
["Computer skill Bu'uuraa"],
["Suphaa TV Decoder & Geepas"]
]

}

class_types = [
["Regular"],
["Weekend"],
["Online"]
]

times = [
["Morning"],
["Afternoon"]
]

locations = [
["Goba"],
["Robe"]
]

def is_admin(user_id):
    return user_id == ADMIN_ID


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    keyboard=[["English","አማርኛ","Afaan Oromoo"]]

    await update.message.reply_text(
    "Choose Language",
    reply_markup=ReplyKeyboardMarkup(keyboard,resize_keyboard=True)
    )

    return LANG


async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):

    lang=language_map.get(update.message.text)

    if not lang:
        return LANG

    context.user_data["lang"]=lang

    await update.message.reply_text(
    "Enter your full name",
    reply_markup=ReplyKeyboardRemove()
    )

    return NAME


async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["name"]=update.message.text

    button=KeyboardButton("Share Phone Number",request_contact=True)

    await update.message.reply_text(
    "Send phone number",
    reply_markup=ReplyKeyboardMarkup([[button]],resize_keyboard=True)
    )

    return PHONE


async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.contact:
        phone=update.message.contact.phone_number
    else:
        phone=update.message.text

    context.user_data["phone"]=phone

    lang=context.user_data["lang"]

    await update.message.reply_text(
    "Choose course",
    reply_markup=ReplyKeyboardMarkup(courses[lang],resize_keyboard=True)
    )

    return COURSE


async def course(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["course"]=update.message.text

    await update.message.reply_text(
    "Choose class type",
    reply_markup=ReplyKeyboardMarkup(class_types,resize_keyboard=True)
    )

    return CLASS


async def class_type(update: Update, context: ContextTypes.DEFAULT_TYPE):

    choice=update.message.text
    context.user_data["class"]=choice

    if choice=="Online":

        context.user_data["time"]="Online"
        context.user_data["location"]="Online"

        return await finish(update,context)

    await update.message.reply_text(
    "Choose time",
    reply_markup=ReplyKeyboardMarkup(times,resize_keyboard=True)
    )

    return TIME


async def time(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["time"]=update.message.text

    await update.message.reply_text(
    "Choose location",
    reply_markup=ReplyKeyboardMarkup(locations,resize_keyboard=True)
    )

    return LOCATION


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["location"]=update.message.text

    return await finish(update,context)


async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data=context.user_data
    user=update.message.from_user

    chat_id=update.message.chat_id
    username=user.username

    registered_users.add(chat_id)

    date=datetime.now().strftime("%Y-%m-%d %H:%M")

    summary=f"""
📌 NEW STUDENT

👤 Name: {data['name']}
📞 Phone: {data['phone']}
📚 Course: {data['course']}
🏫 Class: {data['class']}
⏰ Time: {data['time']}
📍 Location: {data['location']}
👤 Username: @{username}
📅 Date: {date}
"""

    try:
        await context.bot.send_message(CHANNEL_ID,summary)
    except:
        pass

    await update.message.reply_text(summary)

    return ConversationHandler.END


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only command")
        return

    if not context.args:
        await update.message.reply_text("Usage:\n/broadcast message")
        return

    message=" ".join(context.args)

    sent=0

    for user in registered_users:
        try:
            await context.bot.send_message(user,message)
            sent+=1
        except:
            pass

    await update.message.reply_text(f"✅ Broadcast sent to {sent} users")


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(str(update.effective_user.id))


def main():

    app=ApplicationBuilder().token(TOKEN).build()

    conv=ConversationHandler(

    entry_points=[CommandHandler("start",start)],

    states={

    LANG:[MessageHandler(filters.TEXT & ~filters.COMMAND,language)],
    NAME:[MessageHandler(filters.TEXT & ~filters.COMMAND,name)],
    PHONE:[MessageHandler(filters.CONTACT | filters.TEXT,phone)],
    COURSE:[MessageHandler(filters.TEXT & ~filters.COMMAND,course)],
    CLASS:[MessageHandler(filters.TEXT & ~filters.COMMAND,class_type)],
    TIME:[MessageHandler(filters.TEXT & ~filters.COMMAND,time)],
    LOCATION:[MessageHandler(filters.TEXT & ~filters.COMMAND,location)]

    },

    fallbacks=[CommandHandler("start",start)]

    )

    app.add_handler(conv)

    app.add_handler(CommandHandler("broadcast",broadcast))
    app.add_handler(CommandHandler("myid",myid))

    app.run_polling(drop_pending_updates=False)


if __name__=="__main__":
    main()
