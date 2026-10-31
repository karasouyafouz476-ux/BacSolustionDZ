import os
import telebot 
from telebot import types
import requests



TELEGRAM_TOKEN = "8899406527:AAGlWVtQNZMAf8CcWtBtKIqUi1vaG-LZh1k"
GROQ_API_KEY = "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"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

user_branches = {}
BRANCHES = ["لغات اجنبية" ,"اداب وفلسفة" ,"تسيير و اقتصاد" ,"رياضيات" ,"علوم تجريبية","تقني رياضي"]
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [types.KeyboardButton(b) for b in BRANCHES]
    markup.add(*buttons)

    bot.send_message(
        message.chat.id,
            "مرحبا بك يا زميل المستقبل !\n انا استاذك الافتراضي لمساعدتك في البكالوريا.\n اختر شعبتك الدراسية من الازرار بالاسفل :",
            reply_markup=markup )

    
@bot.message_handler(func=lambda message: message.text in BRANCHES)
def set_branch(message):
    user_branches[message.chat.id] = message.text
    bot.reply_to(message, f"تم اعتماد شعبة : **{message.text}** ايمكنك الان ارسال اي سؤال او تمرين و سأقوم بحله لك خطوة بخطوة \n")

@bot.message_handler(func=lambda message : True, content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    branch = user_branches.get(chat_id, "عام")
    bot.send_chat_action(chat_id, 'typing')

    prompt = f"انت استاذ خبير في البكالوريا الجزئرية لشعبة {branch}. قم بحل التمرين او السؤال التالي بدقة و شرح مفصل خطوة بخطوة :\n{message.text}" 

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
                                                               }
        data = { 
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}]
                                                               }   
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers, json=data)
        result = response.json()

        reply_text = result['choices'][0]['message']['contant']
        bot.reply_to(message,reply_text)
    except Exception as e:
        bot.reply_to(message, "عذرا, حدث خطأ في الاتصال.حاول مجددا")

if __name__ == '__main__' :
  print("البوت يعمل بنجاح...")   
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        sent_msg = bot.reply_to(message, "جاري قراءة التمرين وحله !")


        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        image_path = "temp_image.jpg"
        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        response_text ="تم استلام صورة التمرين بنجاح! جاري اعداد الحل ..."

        bot.edit_message_text(
            response_text,
            chat_id=message.chat.id,
            message_id=sent_msg.message_id,
            parse_mode="Markdown"
                                                                                   )                                                           
    except Exception as e:
        bot.reply_to(message, f"حدث خطأ أثناء المعالجة: {str(e)}")

bot.infinity_polling()
    
