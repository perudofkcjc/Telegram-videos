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

# =========================
# TOKEN DEL BOT
# =========================
TOKEN = os.getenv("TOKEN")

# =========================
# FUNCION PRINCIPAL
# =========================
async def reel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text

    await update.message.reply_text("Descargando reel...")

    try:

        # =========================
        # DESCARGAR VIDEO
        # =========================
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': 'video.mp4',
            'quiet': True
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await update.message.reply_text("Buscando mejor captura...")

        # =========================
        # ABRIR VIDEO
        # =========================
        video = cv2.VideoCapture("video.mp4")

        best_frame = None
        best_score = 0

        frame_count = 0

        # =========================
        # ANALIZAR FRAMES
        # =========================
        while True:

            ret, frame = video.read()

            if not ret:
                break

            frame_count += 1

            # Revisar 1 frame cada 10
            if frame_count % 10 != 0:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detectar nitidez
            score = cv2.Laplacian(
                gray,
                cv2.CV_64F
            ).var()

            # Guardar mejor frame
            if score > best_score:
                best_score = score
                best_frame = frame

        video.release()

        # =========================
        # SI NO ENCUENTRA FRAME
        # =========================
        if best_frame is None:
            await update.message.reply_text(
                "No pude encontrar una captura."
            )
            return

        # =========================
        # GUARDAR IMAGEN HD
        # =========================
        cv2.imwrite(
            "captura_hd.png",
            best_frame,
            [cv2.IMWRITE_PNG_COMPRESSION, 0]
        )

        # =========================
        # ENVIAR FOTO
        # =========================
        await update.message.reply_photo(
            photo=open("captura_hd.png", "rb"),
            caption="Captura HD lista"
        )

        # =========================
        # BORRAR ARCHIVOS
        # =========================
        if os.path.exists("video.mp4"):
            os.remove("video.mp4")

        if os.path.exists("captura_hd.png"):
            os.remove("captura_hd.png")

    except Exception as e:

        await update.message.reply_text(
            f"Error:\n{str(e)}"
        )

# =========================
# INICIAR BOT
# =========================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        reel
    )
)

print("BOT ONLINE")

app.run_polling()
