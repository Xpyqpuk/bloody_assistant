import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler

import xlsx_parsing

PASTA = """List of all available commands:\n
/start - show this message
/help - yet again, show this message
/listall - list all previous donations
/getinfo - get information about spesific donation
/addinfo - add donation fact with all information"""

TYPING_DATE, TYPING_INFO = range(2)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=PASTA)

async def listall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_html(f"Below are dates of all your previous donations:\n{xlsx_parsing.list_all_dates(xlsx_parsing.ws)}")

async def getinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter the date in `%d-%m-%Y` format so I can find some info on it")
    return TYPING_DATE

async def received_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_html(xlsx_parsing.get_info_by_date(update.message.text))
    return ConversationHandler.END

async def received_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_html(xlsx_parsing.add_info(update.message.text))
    return ConversationHandler.END

async def addinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_html("Enter values like this <code>23-12-2023,1,156,42.5,244,4.2,210</code> for them to be added")
    return TYPING_INFO

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command")

if __name__ == '__main__':
    application = ApplicationBuilder().token('6727071919:AAG6imQoKex0WZZ2ABw9q540MuYmJgu2_-Y').build()
    
    start_handler = CommandHandler(['start','help'], start)
    listall_handler = CommandHandler('listall', listall)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('getinfo', getinfo),CommandHandler('addinfo',addinfo)],
        states={
            TYPING_DATE: [MessageHandler(filters.TEXT, received_date)],
            TYPING_INFO: [MessageHandler(filters.TEXT, received_info)]
        },
        fallbacks=[]
    )
    addinfo_handler = CommandHandler('addinfo', addinfo)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    application.add_handler(listall_handler)
    application.add_handler(conv_handler)
    application.add_handler(addinfo_handler)
    application.add_handler(unknown_handler)
    
    application.run_polling()
