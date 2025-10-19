
import os
import logging
import re
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# === AMBIL TOKEN DARI ENV ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Environment variable BOT_TOKEN is required!")

# === LINK RESMI SESUAI KNOWLEDGE BASE ===
LINK_DAFTAR = "https://halolink.xyz/s/u/AGENJITU303"
LINK_ADMIN = "https://t.me/agenjitu303"
LINK_PROMO = "https://halolink.xyz/s/u/PROMOSI"
LINK_LOGIN = "https://halolink.xyz/s/u/AGENJITU303"

# Daftar kata/link yang dianggap sensitif (bisa dikembangkan)
SENSITIVE_KEYWORDS = [
    "judi", "slot", "casino", "poker", "agen303", "link", "http", "https",
    "wa.me", "t.me", "free", "hadiah", "klik", "promo", "bonus", "0812", "0856", "penipu", "scam",
    "pepek", "kontol", "memek", "ngentod", "jembut", "bajingan", "anjing", "babi", "tai", "tolol", "goblok", "bangsat"
 
]
# Pola regex untuk deteksi nomor HP (Indonesia)
PHONE_PATTERN = re.compile(r'(\+62|62|08)[0-9]{9,13}')

# === COOLDOWN 12 JAM PER USER ===
last_welcome_time = {}
COOLDOWN_SECONDS = 12 * 60 * 60  # 12 jam

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# === FUNGSI BANTU ===
def is_sensitive(text: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    if any(word in text_lower for word in SENSITIVE_KEYWORDS):
        return True
    if PHONE_PATTERN.search(text):
        return True
    if re.search(r'https?://[^\s]+', text):
        return True
    return False

def detect_violation_reason(text: str) -> str:
    text_lower = text.lower()
    for word in SENSITIVE_KEYWORDS:
        if word in text_lower:
            return f"mengandung kata terlarang: \"{word}\""
    if PHONE_PATTERN.search(text):
        return "mengandung nomor telepon"
    if re.search(r'https?://[^\s]+', text):
        return "mengandung tautan eksternal"
    return "konten tidak sesuai aturan"

def is_on_cooldown(user_id: int) -> bool:
    now = time.time()
    last = last_welcome_time.get(user_id)
    return last is not None and (now - last) < COOLDOWN_SECONDS

def set_cooldown(user_id: int):
    last_welcome_time[user_id] = time.time()

# === SAMBUTAN SAAT USER KIRIM PESAN (/start atau pesan apa pun) ===
async def send_welcome_and_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat = update.effective_chat

    # Abaikan bot lain
    if user.is_bot:
        return

    # Abaikan admin/pemilik
    is_admin = False
    try:
        admins = await context.bot.get_chat_administrators(chat.id)
        admin_ids = {admin.user.id for admin in admins}
        if user.id in admin_ids:
            is_admin = True
    except:
        pass

    # 🔴 JIKA ANGGOTA & PESAN SENSITIF → HAPUS
    if not is_admin and is_sensitive(update.message.text):
        try:
            await update.message.delete()
            logging.info(f"🗑️ Pesan sensitif dari {user.id} dihapus.")
        except:
            pass

        mention = user.mention_html() if user.username else f"<a href='tg://user?id={user.id}'>{user.full_name}</a>"
        reason = detect_violation_reason(update.message.text)
        warning = (
            "⚠️ <b>PERINGATAN OTOMATIS</b>\n\n"
            f"Pesan dari {mention} (ID: <code>{user.id}</code>) telah dihapus karena {reason}.\n\n"
            "Mohon patuhi aturan grup."
        )
        try:
            await context.bot.send_message(chat.id, warning, parse_mode="HTML")
        except:
            pass
        return

    # 🟢 JIKA ADMIN → BIARKAN LEWAT (TIDAK KIRIM SAMBUTAN)
    if is_admin:
        return

    # 🟢 JIKA ANGGOTA & TIDAK SENSITIF → CEK COOLDOWN
    if is_on_cooldown(user.id):
        return  # Diam, jangan kirim apa-apa

    # Kirim sambutan + tombol
    await update.message.reply_text(
        f"Halo Bosku..., {user.first_name}! 👋\n\n"
        "🔥PROMO TERKINI:\n\n"
        "• Bonus New Member 50% (Khusus Slot)\n"
        "• Bonus Deposit Harian 5%\n"
        "• Rollingan Slot 0.5% | Live Casino & Pragmatic Play Up to 1%\n"
        "• Cashback Slot Up to 10%\n"
        "• Bonus Referral 0,1%\n"
        "• Minimal Deposit: Rp1.000 | Withdraw: Rp50.000\n\n"
        "📌Klaim bonus dalam 24 jam setelah deposit pertama!"
    )

    keyboard = [
        [
            InlineKeyboardButton("DAFTAR", url=LINK_DAFTAR),
            InlineKeyboardButton("ADMIN", url=LINK_ADMIN)
        ],
        [
            InlineKeyboardButton("LOGIN", url=LINK_LOGIN),
            InlineKeyboardButton("PROMO", url=LINK_PROMO)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Silakan pilih opsi penting di bawah ini:", reply_markup=reply_markup)

    set_cooldown(user.id)
    logging.info(f"✅ Sambutan dikirim ke {user.id}.")

# === JALANKAN BOT ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_welcome_and_buttons))
    print("✅ Bot aktif! Fitur: moderasi, sambutan 1x/12 jam, 4 tombol link.")
    app.run_polling()

if __name__ == '__main__':
    main()
