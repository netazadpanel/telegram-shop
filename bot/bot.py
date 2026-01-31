from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import requests
from config import BOT_TOKEN

API_URL = "http://127.0.0.1:5000/api"


# ---------------------- شروع ----------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("محصولات تک", callback_data="single")],
        [InlineKeyboardButton("محصولات چند", callback_data="multi")]
    ]
    await update.message.reply_text("سلام! یک دسته را انتخاب کن:", reply_markup=InlineKeyboardMarkup(keyboard))


# ---------------------- انتخاب دسته ----------------------

async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category = query.data

    # دریافت لیست محصولات از پنل
    r = requests.get(f"{API_URL}/products/{category}")
    products = r.json()["products"]

    keyboard = []
    for p in products:
        keyboard.append([InlineKeyboardButton(p["image_url"], callback_data=f"buy_{category}_{p['id']}")])

    await query.edit_message_text("یک محصول انتخاب کن:", reply_markup=InlineKeyboardMarkup(keyboard))


# ---------------------- خرید محصول ----------------------

async def buy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, category, pid = query.data.split("_")
    pid = int(pid)

    user_id = query.from_user.id

    # ثبت سفارش در پنل
    requests.post(f"{API_URL}/new_order", json={
        "user_id": user_id,
        "category": category,
        "product_id": pid
    })

    await query.edit_message_text("سفارش ثبت شد و در انتظار تایید ادمین است.")


# ---------------------- API دریافت لینک دانلود ----------------------

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/send_download", methods=["POST"])
def send_download():
    data = request.json
    user_id = data["user_id"]
    link = data["download_link"]

    import asyncio
    asyncio.run(send_download_to_user(user_id, link))

    return jsonify({"status": "sent"})


async def send_download_to_user(user_id, link):
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    await app.bot.send_message(chat_id=user_id, text=f"سفارش شما تایید شد.\n\nلینک دانلود:\n{link}")


# ---------------------- اجرا ----------------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(category_handler, pattern="^(single|multi)$"))
    app.add_handler(CallbackQueryHandler(buy_handler, pattern="^buy_"))

    app.run_polling()


if __name__ == "__main__":
    main()
    app.run(port=8000)