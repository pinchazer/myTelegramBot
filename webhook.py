# https://api.telegram.org/bot992561955:AAEbZ8e5UzS1qGa4LBEOKDg6tJfigzl9GDo/setWebhook?url=pinchaze.pythonanywhere.com/:88/992561955:AAEbZ8e5UzS1qGa4LBEOKDg6tJfigzl9GDo
from flask import Flask
from flask import request
from flask import jsonify
from flask_sslify import SSLify
from queue import Queue  # in python 2 it should be "from Queue"
from threading import Thread
import logging
import telegram
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
sslify = SSLify(app)

TOKEN = "992561955:AAEbZ8e5UzS1qGa4LBEOKDg6tJfigzl9GDo"
my_webhook_url = 'https://199cf81e.ngrok.io'
port = '88'

# Stages
DOLLAR_SIG, EURO_SIG, DEL_DOLL, DEL_EUR = range(4)

def signals_markup_reply():
    keyboard = [
        [InlineKeyboardButton("Сигнал $", callback_data=str(DOLLAR_SIG)),
         InlineKeyboardButton("Сигнал \u20AC", callback_data=str(EURO_SIG))],
        [InlineKeyboardButton("Удалить", callback_data=str(DEL_DOLL)),
         InlineKeyboardButton("Удалить", callback_data=str(DEL_EUR))]
    ]
    return InlineKeyboardMarkup(keyboard)

def start(update, context):

    custom_keyboard = [['Курс $', 'Курс \u20AC'],
                       ['Установить/удалить сигналы', 'Выход']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

    update.message.reply_text(
        "Я могу предоставить информацию о курсах валют, а так же установить сигналы",
        reply_markup=reply_markup
    )

def close(update, context):
    reply_markup = telegram.ReplyKeyboardRemove()
    update.message.reply_text(
        "До встречи! Для работы команда /start",
        reply_markup=reply_markup
    )

def dollar(update, context):
    update.message.reply_text("dollar")
    #TODO show dollar
    pass

def euro(update, context):
    update.message.reply_text("euro")
    #TODO show euro
    pass

def signals_menu(update, context):
    update.message.reply_text("Выберите действие:", reply_markup=signals_markup_reply())

def del_dol(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите действие:\nсигнал для $ удален', reply_markup=signals_markup_reply())
    # TODO reset signal
    pass

def del_eur(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите действие:\nсигнал для \u20AC удален', reply_markup=signals_markup_reply())
    # query.message.reply_text('сигнал для \u20AC удален')
    # TODO reset signal
    pass

def signal_dol(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    logger.info("User %s started the conversation.", user.first_name)
    query.message.reply_text("Напишите курс $, для которого устанавливаете сигнал")
    return DOLLAR_SIG

def signal_eur(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    logger.info("User %s started the conversation.", user.first_name)
    query.message.reply_text("Напишите курс \u20AC, для которого устанавливаете сигнал")
    return EURO_SIG

def signal_dol_setup(update, context):  # part of ConversationHandler
    update.message.reply_text("signal_dol_setup")

def signal_eur_setup(update, context):  # part of ConversationHandler
    update.message.reply_text("signal_eur_setup")

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def setup(token):
    # Create bot, update queue and dispatcher instances
    bot = Bot(token)
    if bot.getWebhookInfo()['url'] != my_webhook_url:
        bot.set_webhook(webhook_url='{0}/:{1}/{2}'.format(my_webhook_url, port, TOKEN))
    update_queue = Queue()

    dispatcher = Dispatcher(bot, update_queue, use_context=True)

    ##### Register handlers here #####

    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(signal_dol, pattern='^' + str(DOLLAR_SIG) + '$'),
            CallbackQueryHandler(signal_eur, pattern='^' + str(EURO_SIG) + '$')
        ],
        states={
            DOLLAR_SIG: [MessageHandler(Filters.regex('^[0-9]+\.[0-9]+$'), signal_dol_setup)],
            EURO_SIG: [MessageHandler(Filters.regex('^[0-9]+\.[0-9]+$'), signal_eur_setup)]
        },
        fallbacks=[
            MessageHandler(Filters.regex('^Выход$'), close)
        ]
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(MessageHandler(Filters.regex('^Курс \u20AC$'), euro))
    dispatcher.add_handler(MessageHandler(Filters.regex('^Курс \$$'), dollar))
    dispatcher.add_handler(CallbackQueryHandler(del_dol, pattern='^'+str(DEL_DOLL)+'$'))
    dispatcher.add_handler(CallbackQueryHandler(del_eur, pattern='^'+str(DEL_EUR)+'$'))
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.regex('^Установить/удалить сигналы$'), signals_menu))
    dispatcher.add_handler(MessageHandler(Filters.regex('^Выход$'), close))
    dispatcher.add_error_handler(error)

    # Start the thread
    thread = Thread(target=dispatcher.start, name='dispatcher')
    thread.start()

    # return update_queue
    # you might want to return dispatcher as well,
    # to stop it at server shutdown, or to register more handlers:
    return (update_queue, dispatcher)


update_queue, dp = setup(TOKEN)


@app.route('/')
def hello_world():
    return '<p style="text-align: center;"><strong>КУКУ)</strong></p>'


@app.route('/:88/' + TOKEN, methods=["POST", "GET"])
def webhook():
    if request.method == 'POST':
        gjson = request.get_json()
        update = Update.de_json(gjson, dp.bot)
        update_queue.put(update)
        return jsonify(gjson)
    else:
        return '<p style="text-align: center;"><strong>OK)</strong></p>'


if __name__ == '__main__':
    app.run()
