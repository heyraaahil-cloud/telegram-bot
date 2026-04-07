import telebot
from telebot import types
import yt_dlp
import instaloader
import os
from flask import Flask
import threading

# 🔑 PUT YOUR TOKEN HERE
BOT_TOKEN = '8674483372:AAEZ9W4emk4BE5Pf1EF0NV9Rqkg9v1QC3Vc'

bot = telebot.TeleBot(BOT_TOKEN)

# 🌐 FAKE WEB SERVER (FOR RENDER)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def run_web():
    app.run(host="0.0.0.0", port=10000)

# 🟢 START MENU (INLINE BUTTONS)
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🎵 Music", callback_data="music"),
        types.InlineKeyboardButton("📸 Reels", callback_data="reels")
    )

    bot.send_message(
        message.chat.id,
        "🔥 Welcome!\n\nChoose an option:",
        reply_markup=markup
    )

# 🟢 BUTTON HANDLER
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):

    if call.data == "music":
        msg = bot.send_message(call.message.chat.id, "🎵 Send song name:")
        bot.register_next_step_handler(msg, download_music)

    elif call.data == "reels":
        msg = bot.send_message(call.message.chat.id, "📸 Send Instagram reel link:")
        bot.register_next_step_handler(msg, download_reel)

    elif call.data == "back":
        start(call.message)

# 🎵 MUSIC DOWNLOAD
def download_music(message):
    query = message.text
    status = bot.send_message(message.chat.id, "⏳ Searching...")

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'song.%(ext)s',
            'quiet': True,
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            title = info['entries'][0]['title']

        bot.edit_message_text("📥 Uploading...", message.chat.id, status.message_id)

        with open("song.mp3", "rb") as f:
            bot.send_audio(message.chat.id, f, title=title)

        os.remove("song.mp3")

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Back to Menu", callback_data="back"))

        bot.send_message(message.chat.id, f"✅ Done: {title}", reply_markup=markup)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

# 📸 REEL DOWNLOAD
def download_reel(message):
    url = message.text
    status = bot.send_message(message.chat.id, "⏳ Downloading reel...")

    try:
        L = instaloader.Instaloader(dirname_pattern='reel')

        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target='reel')

        for file in os.listdir("reel"):
            if file.endswith(".mp4"):
                bot.edit_message_text("📥 Uploading...", message.chat.id, status.message_id)

                with open(f"reel/{file}", "rb") as f:
                    bot.send_video(message.chat.id, f)

                os.remove(f"reel/{file}")

        os.rmdir("reel")

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Back to Menu", callback_data="back"))

        bot.send_message(message.chat.id, "✅ Reel sent!", reply_markup=markup)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

print("🚀 Bot is running...")

# 🚀 RUN BOTH BOT + WEB SERVER
threading.Thread(target=run_web).start()
bot.infinity_polling()
