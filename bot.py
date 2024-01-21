import logging
from telegram import ForceReply, ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
import downloader
import main
import time

logging.basicConfig(

    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO

)

downloading = 1

reply_keyboard = ReplyKeyboardMarkup([["/download"]], one_time_keyboard=True)

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.username
    await update.message.chat.send_message(main.replics["start"].format(user), reply_markup=reply_keyboard)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_message(main.replics["help"], reply_markup=reply_keyboard)


async def begin_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(main.replics["enter_link"])

    return downloading


async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(main.replics["try_download"])

    result = downloader.download_video_via_url(update.message.text)

    if result == -2:
        await update.message.reply_text(main.replics["wrong_link"])
        return ConversationHandler.END
    elif result == -1:
        await update.message.reply_text(main.replics["too_long"].format(time.strftime("%H:%M:%S", time.gmtime(main.config["max_duration"]))))
        return ConversationHandler.END
    
    audio_file = "temp/{}.m4a".format(result)
    title_file = "temp/{}.txt".format(result)
    title = ""

    with open(title_file, "r") as f:
        title = f.read()

    await update.message.reply_text(main.replics["sending"])

    try:
        await update.message.chat.send_audio(audio=open(audio_file, "rb"), title=title, filename="{}.m4a".format(title), reply_markup=reply_keyboard)
    except:
        await update.message.reply_text(main.replics["failed_to_send"])
        try:
            await update.message.chat.send_audio(audio=open(audio_file, "rb"), title=title, filename="{}.m4a".format(title), reply_markup=reply_keyboard)
        except:
            await update.message.reply_text(main.replics["fatal_failed_to_send"])

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(main.replics["cancel"])
    return ConversationHandler.END


def start_bot() -> None:
    app = Application.builder().token(main.config["token"]).read_timeout(20).build()
    
    app.add_handler(CommandHandler(["start", "help"], start))

    conv_handler = ConversationHandler(entry_points=[CommandHandler("download", begin_download)],
    states={downloading: [MessageHandler(filters.TEXT, download)]},
    fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)

    app.run_polling()

if __name__ == "__main__":
    main()
