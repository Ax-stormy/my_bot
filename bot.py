import os, telebot, yt_dlp
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "@hammel5Bblash"
CHANNEL_LINK = "https://t.me/hammel5Bblash"
bot = telebot.TeleBot(TOKEN)
user_links = {}
def is_sub(uid):
    try:
        s = bot.get_chat_member(CHANNEL_ID, uid).status
        return s in ['creator','administrator','member']
    except: return False
@bot.message_handler(commands=['start'])
def start(m):
    if not is_sub(m.from_user.id):
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("📢 اشترك", url=CHANNEL_LINK))
        mk.add(InlineKeyboardButton("✅ تحققت", callback_data="check"))
        bot.send_message(m.chat.id, "❗ اشترك الاول", reply_markup=mk)
        return
    bot.send_message(m.chat.id, "ابعت لينك")
@bot.message_handler(func=lambda m: m.text and "http" in m.text)
def link_handler(m):
    if not is_sub(m.from_user.id):
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("📢 اشترك", url=CHANNEL_LINK))
        bot.send_message(m.chat.id, "❗ مش مشترك", reply_markup=mk)
        return
    user_links[m.from_user.id] = m.text.strip()
    mk = InlineKeyboardMarkup(row_width=2)
    mk.add(InlineKeyboardButton("🎥 فيديو", callback_data="vid"), InlineKeyboardButton("🎵 اغنية", callback_data="aud"))
    bot.send_message(m.chat.id, "اختار:", reply_markup=mk)
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    if c.data == "check":
        if is_sub(c.from_user.id): bot.send_message(c.message.chat.id, "✅ ابعت اللينك")
        else: bot.send_message(c.message.chat.id, "❌ لسه")
        return
    url = user_links.get(c.from_user.id)
    if not url: return
    if c.data == "vid":
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("🔥 افضل جودة", callback_data="dl_best"))
        mk.add(InlineKeyboardButton("720p", callback_data="dl_720"), InlineKeyboardButton("480p", callback_data="dl_480"))
        bot.edit_message_text("اختار الجودة:", c.message.chat.id, c.message.message_id, reply_markup=mk)
    elif c.data == "aud":
        bot.edit_message_text("⏳ بحول لـ mp3...", c.message.chat.id, c.message.message_id)
        do_download(c.message.chat.id, url, "aud", "best")
    elif c.data.startswith("dl_"):
        q = c.data.replace("dl_", "")
        bot.edit_message_text(f"⏳ بحمل {q}...", c.message.chat.id, c.message.message_id)
        do_download(c.message.chat.id, url, "vid", q)
def do_download(chat_id, url, typ, q):
    import os
    for f in os.listdir('.'):
        if f.startswith("dl_"):
            try: os.remove(f)
            except: pass
    if typ == "aud":
        opts = {'format': 'bestaudio[ext=m4a]/bestaudio/best', 'outtmpl': 'dl_a.%(ext)s', 'quiet': True, 'noplaylist': True, 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '128'}]}
    else:
        fmt = "best" if q=="best" else f"bestvideo[height<={q}]+bestaudio/best[height<={q}]/best"
        opts = {'format': fmt, 'outtmpl': 'dl_v.%(ext)s', 'quiet': True, 'noplaylist': True, 'merge_output_format': 'mp4'}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([url])
        for f in os.listdir('.'):
            if f.startswith("dl_"):
                with open(f,'rb') as file:
                    if typ=="aud": bot.send_audio(chat_id, file, timeout=120)
                    else: bot.send_video(chat_id, file, timeout=120)
                os.remove(f)
                return
    except Exception as e:
        bot.send_message(chat_id, f"ايرور: {e}")
print("Bot Running...")
bot.infinity_polling()
