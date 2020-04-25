import logging
import dataobtain
import telegram

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def start(update, context):
    update.message.reply_text("Здарова, просто нажми на эту хрень /kurs")



def kurs(update, context):
    caption = 'Текущий курс {}'.format(dataobtain.priceNow)
    dataobtain.draw_pic(dataobtain.dfUSDRUB)
    with open(r'pic.png', 'rb') as f:
        update.message.reply_photo(photo=f, caption=caption)

def callback_minute(context):
    context.bot.send_message(chat_id=context.job.context, text='дарова')

def teller(update, context):
    context.job_queue.run_repeating(callback_minute, 3, context=update.message.chat_id)

def main():

    TOKEN = "992561955:AAEbZ8e5UzS1qGa4LBEOKDg6tJfigzl9GDo"

    updater = Updater(TOKEN, use_context=True)
    # add handlers

    dp = updater.dispatcher
    #j = updater.job_queue

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('kurs', kurs))
    #dp.add_handler(CommandHandler('tell', teller))
    #j.run_repeating(callback_minute, interval=3, first=0, context=)

    #dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()


    #updater.idle()