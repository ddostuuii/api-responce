import asyncio
import nest_asyncio  # AsyncIO Issues Fix
import requests
import json
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes, CallbackQueryHandler

nest_asyncio.apply()  # Async Issues Fix

# Telegram Bot Token (अपना बॉट टोकन यहाँ डालें)
TOKEN = "7154780966:AAEH5oP5qt_cpxGnsaeYke2u9LKIlBPRUM8"

# Channel ID (अपने चैनल का Chat ID यहाँ डालें, जैसे: -1001234567890)
CHANNEL_ID = -1002413736903  

# Conversation states
URL, JSON_DATA = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """बॉट स्टार्ट होने पर यूज़र से URL माँगता है और मैसेज चैनल में फॉरवर्ड करता है।"""
    
    keyboard = [["Cancel"], ["Help"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "Welcome! Please enter the URL where you want to send a request:",
        reply_markup=reply_markup,
    )

    await forward_to_channel(update, context)  # चैनल में फॉरवर्ड करें
    return URL

async def get_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """यूज़र से URL लेता है और JSON डेटा माँगता है।"""
    context.user_data["url"] = update.message.text.strip()
    
    await update.message.reply_text("Now, enter the JSON data:")
    await forward_to_channel(update, context)  # चैनल में फॉरवर्ड करें

    return JSON_DATA

async def get_json_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """यूज़र से JSON डेटा लेकर API पर POST request भेजता है।"""
    user_input = update.message.text.strip()

    try:
        data = json.loads(user_input)  # JSON string to dictionary
    except json.JSONDecodeError:
        await update.message.reply_text("❌ Invalid JSON format! Please enter valid JSON data.")
        return JSON_DATA  # दुबारा पूछे

    url = context.user_data["url"]
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=data, headers=headers)
        await update.message.reply_text(f"✅ Response:\n{response.text}")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"❌ Error: {e}")

    await forward_to_channel(update, context)  # चैनल में फॉरवर्ड करें
    await update.message.reply_text("Send another request? Type /start to begin again.")
    return ConversationHandler.END

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline Keyboard के लिए Callback हैंडल करता है।"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "help":
        await query.message.reply_text("Here is how you can use this bot:\n1️⃣ Send a URL\n2️⃣ Provide JSON data\n3️⃣ Get API response!")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unknown commands के लिए।"""
    await update.message.reply_text("❓ I didn't understand that command. Use /start to begin.")
    await forward_to_channel(update, context)  # चैनल में फॉरवर्ड करें

async def forward_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """हर चैट (प्राइवेट/ग्रुप) के सभी मैसेज को चैनल में फॉरवर्ड करता है।"""
    message = update.message

    if message:
        try:
            await context.bot.forward_message(
                chat_id=CHANNEL_ID,  # चैनल में फॉरवर्ड करें
                from_chat_id=message.chat_id,  # जिस चैट से मैसेज आया है
                message_id=message.message_id
            )
        except Exception as e:
            print(f"Error forwarding message: {e}")

async def main():
    """Telegram बॉट को स्टार्ट करता है।"""
    app = Application.builder().token(TOKEN).build()

    # Conversation Handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            URL: [MessageHandler(filters.ALL, get_url)],  # सभी मैसेज से URL एक्सेप्ट करें
            JSON_DATA: [MessageHandler(filters.ALL, get_json_data)],  # सभी मैसेज से JSON डेटा एक्सेप्ट करें
        },
        fallbacks=[],
    )

    # हैंडलर्स ऐड करें
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))  # Unknown command handler
    app.add_handler(MessageHandler(filters.ALL, forward_to_channel))  # सभी मैसेज को फॉरवर्ड करने वाला हैंडलर

    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())  # Async Mode में बॉट रन करेगा
