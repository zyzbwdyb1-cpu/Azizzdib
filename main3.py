import os
import asyncio
from pyrogram import Client, filters
from yt_dlp import YoutubeDL
from pyrogram.types import Message

# ========= إعداد متغيرات البيئة =========
API_ID = int(os.getenv("API_ID", "22778893"))  # ضع API_ID هنا إن لم تستخدم ENV
API_HASH = os.getenv("API_HASH", "04284c11d0fffa4668cf020a8bce447b")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7993762933:AAFLvxefBiOaiEIiO3To_JBVa0LiB2R6nY8")

# ========= إعداد البوت =========
bot = Client(
    "MusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ========= إعداد اليوتيوب =========
ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'nocheckcertificate': True,
    'extract_flat': False,
    'outtmpl': '%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

# ========= أمر تشغيل الأغنية =========
@bot.on_message(filters.command(["استمع", "شغل", "play"]) & filters.group)
async def play_music(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("🎵 أرسل اسم الأغنية بعد كلمة استمع.\nمثال:\n`استمع Despacito`")
        return

    query = " ".join(message.command[1:])
    await message.reply_text(f"⏳ جاري البحث عن: `{query}` ...")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            url = info['url']
            title = info.get('title', 'Audio')
            duration = info.get('duration', 0)

        await message.reply_audio(
            audio=url,
            title=title,
            caption=f"🎶 **{title}**\n⏱ المدة: {duration//60}:{duration%60:02d}\n✅ تشغيل أونلاين",
            performer="Music Bot"
        )
    except Exception as e:
        await message.reply(f"❌ حدث خطأ أثناء جلب الأغنية:\n`{str(e)}`")

# ========= بدء تشغيل البوت =========
print("🎵 Music MP3 Bot is running...")
bot.run()..."