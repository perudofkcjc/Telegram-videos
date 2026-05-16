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
        best_score = -999999

        frame_count = 0

        # =========================
        # ANALIZAR FRAMES
        # =========================
        while True:

            ret, frame = video.read()

            if not ret:
                break

            frame_count += 1

            # revisar 1 frame cada 10
            if frame_count % 10 != 0:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # =========================
            # DETECTAR NITIDEZ
            # =========================
            sharpness = cv2.Laplacian(
                gray,
                cv2.CV_64F
            ).var()

            # =========================
            # DETECTAR OBJETOS GRANDES
            # =========================
            h, w = gray.shape

            center = gray[
                h//4:3*h//4,
                w//4:3*w//4
            ]

            edges = cv2.Canny(
                center,
                100,
                200
            )

            object_score = edges.sum()

            # =========================
            # SCORE FINAL
            # =========================
            score = sharpness - (object_score * 0.02)

            # guardar mejor frame
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
        # MEJORAR CALIDAD
        # =========================
        best_frame = cv2.detailEnhance(
            best_frame,
            sigma_s=10,
            sigma_r=0.15
        )

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
