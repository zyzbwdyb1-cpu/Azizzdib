import os
import yt_dlp
import asyncio
from pyrogram import Client, filters
import logging
from flask import Flask
import threading

# تفعيل التسجيل للكشف عن الأخطاء
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# بيانات البوت من متغيرات البيئة
API_ID = int(os.environ.get("API_ID", 22778893))
API_HASH = os.environ.get("API_HASH", "04284c11d0fffa4668cf020a8bce447b")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7993762933:AAFLvxefBiOaiEIiO3To_JBVa0LiB2R6nY8")

# المسار المؤقت للتخزين
DOWNLOAD_PATH = "downloads/"

# إنشاء المسار إذا لم يكن موجوداً
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# إنشاء تطبيق Flask لخدمة الويب
app = Flask(__name__)

@app.route('/')
def home():
    return "🎵 Music Bot is Running! Send /start to the bot."

@app.route('/health')
def health():
    return "✅ Bot is healthy and running!"

# تهيئة البوت
bot = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def download_audio(query):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'verbose': True,
            'socket_timeout': 60,
            'retries': 10,
            'fragment_retries': 10,
        }
        
        logger.info(f"بدء تحميل: {query}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)
            if not info or 'entries' not in info or not info['entries']:
                logger.error("لم يتم العثور على نتائج")
                return None, None
                
            video_info = info['entries'][0]
            filename = ydl.prepare_filename(video_info)
            mp3_filename = os.path.splitext(filename)[0] + '.mp3'
            
            logger.info(f"تم التحميل: {mp3_filename}")
            return mp3_filename, video_info['title']
            
    except Exception as e:
        logger.error(f"خطأ في التحميل: {str(e)}")
        return None, None

@bot.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply("🎵 **أهلاً! أنا بوت الموسيقى**\n\nاكتب: `استمع اسم_الأغنية`")

@bot.on_message(filters.command("استمع"))
async def play_song(client, message):
    try:
        query = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else None
        if not query:
            await message.reply("🎵 **يرجى كتابة اسم الأغنية بعد الأمر استمع**")
            return

        progress_msg = await message.reply("🔎 **جاري البحث عن الأغنية...**")
        
        try:
            file_path, title = await asyncio.wait_for(
                asyncio.to_thread(download_audio, query),
                timeout=60.0
            )
        except asyncio.TimeoutError:
            await progress_msg.edit("⏰ **انتهت مهلة التحميل (60 ثانية). يرجى المحاولة مرة أخرى.**")
            return

        if file_path and os.path.exists(file_path):
            await progress_msg.edit("📤 **جاري إرسال الأغنية...**")
            await message.reply_audio(
                audio=file_path,
                title=title or "أغنية",
                performer="Music Bot",
                caption=f"🎶 **{title or 'أغنية'}**\n✅ تم التحميل بنجاح"
            )
            os.remove(file_path)
            await progress_msg.delete()
        else:
            await progress_msg.edit("❌ **لم أستطع العثور على الأغنية أو تحميلها.**")
            
    except IndexError:
        await message.reply("🎵 **يرجى كتابة اسم الأغنية بعد الأمر استمع**")
    except Exception as e:
        logger.error(f"خطأ غير متوقع: {str(e)}")
        await message.reply("❌ **حدث خطأ غير متوقع أثناء المعالجة.**")

def run_flask():
    """تشغيل خادم Flask في الخلفية"""
    app.run(host='0.0.0.0', port=10000, debug=False)

def run_bot():
    """تشغيل بوت التليجرام"""
    print("🎵 البوت شغال الآن...")
    bot.run()

if __name__ == "__main__":
    # تشغيل Flask في thread منفصل
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # تشغيل البوت
    run_bot()