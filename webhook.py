# https://api.telegram.org/bot1232259102:AAGdytN-3fmnc-BV3Gc9xML568mUeXpgbF8/setWebhook?url=pinchaze.pythonanywhere.com/:88/992561955:AAEbZ8e5UzS1qGa4LBEOKDg6tJfigzl9GDo
# https://api.telegram.org/bot1232259102:AAGdytN-3fmnc-BV3Gc9xML568mUeXpgbF8/getWebhookInfo
from flask import Flask
from flask import request
from flask import jsonify
from flask_sslify import SSLify
from queue import Queue  # in python 2 it should be "from Queue"
from threading import Thread
import logging
import telegram
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
import dataobtain
from datetime import time
from functools import wraps
from telegram import ChatAction
from config import Configuration




# for bot typing...
def send_action(action):
    """Sends `action` while processing func command."""
    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context, *args, **kwargs)
        return command_func
    return decorator



send_typing_action = send_action(ChatAction.TYPING)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
sslify = SSLify(app)

#TOKEN = "1232259102:AAGdytN-3fmnc-BV3Gc9xML568mUeXpgbF8"
#my_webhook_url = 'https://9bbe98be.ngrok.io'
#port = '88'

# Stages
DOLLAR_SIG, EURO_SIG, DEL_DOLL, DEL_EUR = range(4)


def signals_markup_reply():
    """Help function to reduce code"""
    keyboard = [
        [InlineKeyboardButton("Сигнал $", callback_data=str(DOLLAR_SIG)),
         InlineKeyboardButton("Сигнал \u20AC", callback_data=str(EURO_SIG))],
        [InlineKeyboardButton("Удалить", callback_data=str(DEL_DOLL)),
         InlineKeyboardButton("Удалить", callback_data=str(DEL_EUR))]
    ]
    return InlineKeyboardMarkup(keyboard)


def start(update, context):
    """Start message and custom buttons"""
    custom_keyboard = [['Курс $', 'Курс \u20AC'],
                       ['Установить/удалить сигналы', 'Выход']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

    update.message.reply_text("Я могу предоставить информацию о курсах валют, а так же установить сигналы",
                              reply_markup=reply_markup)


def close(update, context):
    """Closing function. Close all signal threads for each user who typed close command"""
    reply_markup = ReplyKeyboardRemove()
    update.message.reply_text(
        "До встречи! Для работы команда /start",
        reply_markup=reply_markup
    )
    for name in ('dollar_routine', 'show_dollar'):
        for jobObj in context.job_queue.get_jobs_by_name(name):
            jobObj.schedule_removal()
    return ConversationHandler.END


@send_typing_action
def dollar(update, context):
    caption = 'Текущий курс доллара <b>{}</b>\nДанные получены с сайта <a href="http://yahoo.com">Yahoo! Finance</a>' \
        .format(dataobtain.show_dollar(context))
    with open(r'picDol.png', 'rb') as f:
        update.message.reply_photo(photo=f, caption=caption, parse_mode=telegram.ParseMode.HTML)


@send_typing_action
def euro(update, context):
    caption = 'Текущий курс евро <b>{}</b>\nДанные получены с сайта <a href="http://yahoo.com">Yahoo! Finance</a>' \
        .format(dataobtain.show_euro(context))
    with open(r'picEur.png', 'rb') as f:
        update.message.reply_photo(photo=f, caption=caption, parse_mode=telegram.ParseMode.HTML)


def signals_menu(update, context):
    update.message.reply_text("Выберите действие:", reply_markup=signals_markup_reply())



def wrong_val_message(update, context):
    update.message.reply_text("Внимание! Введите число с десятичной точкой")


def del_dol(update, context):
    # we always should answer on inline buttons
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите действие:\nсигнал для $ удален', reply_markup=signals_markup_reply())

    context.bot_data['dol_data'].update({update.message.chat_id: None})



def del_eur(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите действие:\nсигнал для \u20AC удален', reply_markup=signals_markup_reply())

    context.bot_data['eur_data'].update({update.message.chat_id: None})




def signal_dol(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    logger.info("User %s started the conversation.", user.first_name)
    query.message.reply_text("Напишите курс $, для которого устанавливаете сигнал\n"
                             "Например 65.44")
    return DOLLAR_SIG


def signal_eur(update, context):
    query = update.callback_query
    query.answer()
    user = query.from_user
    logger.info("User {} started the conversation.".format(user.first_name))
    query.message.reply_text("Напишите курс \u20AC, для которого устанавливаете сигнал\n"
                             "Например 75.78")
    return EURO_SIG


def signal_dol_setup(update, context):  # part of ConversationHandler
    # store signal value to user_data dict
    context.bot_data['dol_data'].update({update.message.chat_id:
                                         {'val': float(update.message.text), 'trig_less': False, 'trig_more': False}
                                     })


    # remove old dollar_routine to make in run again with new signal value
    for jobObj in context.job_queue.get_jobs_by_name('dollar_routine'):
        jobObj.schedule_removal()


    context.job_queue.run_repeating(callback=dataobtain.signal_routine_dollar, interval=20,
                                    first=10, name='dollar_routine', context=context.bot_data)

    update.message.reply_text("Сигнал для доллара установлен")
    # To END conversation
    return ConversationHandler.END


def signal_eur_setup(update, context):  # part of ConversationHandler
    # store signal value to user_data dict
    # context.user_data['eur'] = update.message.text
    context.bot_data['eur_data'].update({update.message.chat_id:
                                         {'val': float(update.message.text), 'trig_less': False, 'trig_more': False}
                                     })
    # remove old euro_routine to make in run again with new signal value
    for jobObj in context.job_queue.get_jobs_by_name('euro_routine'):
        jobObj.schedule_removal()


    context.job_queue.run_repeating(callback=dataobtain.signal_routine_euro, interval=20,
                                    first=10, name='euro_routine', context=context.bot_data)

    update.message.reply_text("Сигнал для евро установлен")
    # To END conversation
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def setup(token):
    # Create bot, update queue and dispatcher instances
    bot = Bot(token)
    # Setup webhook if it was changed
    if bot.getWebhookInfo()['url'] != Configuration.WEBHOOK:
        bot.set_webhook(webhook_url='{0}/:{1}/{2}'.format(Configuration.WEBHOOK, Configuration.PORT, Configuration.TOKEN))
    update_queue = Queue()
    job_queue = telegram.ext.JobQueue()

    dispatcher = Dispatcher(bot, update_queue, use_context=True, job_queue=job_queue)
    job_queue.set_dispatcher(dispatcher)

    ##### Register handlers here #####

    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(signal_dol, pattern='^' + str(DOLLAR_SIG) + '$'),
            CallbackQueryHandler(signal_eur, pattern='^' + str(EURO_SIG) + '$')
        ],
        states={
            DOLLAR_SIG: [MessageHandler(Filters.regex('^[0-9]+\.[0-9]+$'), signal_dol_setup),
                         MessageHandler(Filters.regex('([0-9]+)|([a-zA-Z]+)'), wrong_val_message)],
            EURO_SIG: [MessageHandler(Filters.regex('^[0-9]+\.[0-9]+$'), signal_eur_setup),
                       MessageHandler(Filters.regex('([0-9]+)|([a-zA-Z]+)'), wrong_val_message)]
        },
        fallbacks=[
            MessageHandler(Filters.regex('^Выход$'), close)
        ],
        conversation_timeout=90
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(MessageHandler(Filters.regex('^Курс \u20AC$'), euro))
    dispatcher.add_handler(MessageHandler(Filters.regex('^Курс \$$'), dollar))
    dispatcher.add_handler(CallbackQueryHandler(del_dol, pattern='^' + str(DEL_DOLL) + '$'))
    dispatcher.add_handler(CallbackQueryHandler(del_eur, pattern='^' + str(DEL_EUR) + '$'))
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.regex('^Установить/удалить сигналы$'), signals_menu))
    dispatcher.add_handler(MessageHandler(Filters.regex('^Выход$'), close))
    dispatcher.add_error_handler(error)

    dispatcher.bot_data['dol_data'] = dict()
    dispatcher.bot_data['eur_data'] = dict()

    # Start the thread
    thread = Thread(target=dispatcher.start, name='dispatcher')
    thread.start()

    # return update_queue
    # you might want to return dispatcher as well,
    # to stop it at server shutdown, or to register more handlers:
    return (update_queue, dispatcher)


# use utc time
t = time(hour=6, minute=0, second=0)
update_queue, dp = setup(Configuration.TOKEN)

# daily routine for picture updating
dp.job_queue.run_daily(callback=dataobtain.daily_routine, days=(0, 1, 2, 3, 4),
                       time=t, name='run_daily')

dp.job_queue.start()


@app.route('/')
def hello_world():
    return '<p style="text-align: center;"><strong>КУКУ)</strong></p>'


@app.route('/:88/' + Configuration.TOKEN, methods=["POST", "GET"])
def webhook():
    if request.method == 'POST':
        gjson = request.get_json()
        update = Update.de_json(gjson, dp.bot)
        update_queue.put(update)
        return jsonify(gjson)
    else:
        return '<p style="text-align: center;"><strong>OK)</strong></p>'


if __name__ == '__main__':
    app.run(host='0.0.0.0')
