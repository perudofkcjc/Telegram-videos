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
import re
import urllib.parse
import subprocess

# =========================
# ACTUALIZAR YT-DLP
# =========================
subprocess.run(
    ["pip", "install", "-U", "yt-dlp"],
    check=True
)

# =========================
# TOKEN DEL BOT
# =========================
TOKEN = os.getenv("TOKEN")

# =========================
# FUNCION PRINCIPAL
# =========================
async def reel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()

    # =========================
    # LIMPIAR LINKS LOGIN FACEBOOK
    # =========================
    if "login" in url and "next=" in url:

        match = re.search(r'next=([^&]+)', url)

        if match:
            url = urllib.parse.unquote(
                match.group(1)
            )

    await update.message.reply_text(
        "Descargando reel..."
    )

    try:

        # =========================
        # DESCARGAR VIDEO
        # =========================
        ydl_opts = {
            'format': 'bv*+ba/b',
            'outtmpl': 'video.mp4',
            'quiet': False,
            'noplaylist': True
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await update.message.reply_text(
            "Buscando mejor captura..."
        )

        # =========================
        # ABRIR VIDEO
        # =========================
        video = cv2.VideoCapture(
            "video.mp4"
        )

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

            # revisar más frames
            if frame_count % 5 != 0:
                continue

            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

            # =========================
            # DETECTAR NITIDEZ
            # =========================
            sharpness = cv2.Laplacian(
                gray,
                cv2.CV_64F
            ).var()

            # =========================
            # DETECTAR MOVIMIENTO
            # =========================
            blur = cv2.GaussianBlur(
                gray,
                (9, 9),
                0
            )

            motion = cv2.Laplacian(
                blur,
                cv2.CV_64F
            ).var()

            # =========================
            # IGNORAR FRAMES MOVIDOS
            # =========================
            if motion > 500:
                continue

            # =========================
            # SCORE FINAL
            # =========================
            score = sharpness

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
                "No encontré una captura limpia."
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
            photo=open(
                "captura_hd.png",
                "rb"
            ),
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
