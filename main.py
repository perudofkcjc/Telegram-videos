from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters
)

from yt_dlp import YoutubeDL
import cv2
import os

TOKEN = os.getenv("TOKEN")

async def reel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text

    try:

        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.mp4'
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        video = cv2.VideoCapture("video.mp4")

        # segundo exacto
        video.set(cv2.CAP_PROP_POS_MSEC, 2000)

        ok, frame = video.read()

        if ok:

            cv2.imwrite("captura.png", frame)

            await update.message.reply_photo(
                photo=open("captura.png", "rb"),
                caption="Captura HD lista"
            )

        video.release()

        if os.path.exists("video.mp4"):
            os.remove("video.mp4")

        if os.path.exists("captura.png"):
            os.remove("captura.png")

    except Exception as e:
        await update.message.reply_text(str(e))

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, reel)
)

print("BOT ONLINE")

app.run_polling()