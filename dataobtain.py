import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator, AutoLocator
import pandas as pd


from datetime import datetime, timezone, time
from time import sleep
from telegram.ext import Dispatcher

#USDRUB = yf.Ticker("RUB=X")
#priceNow = round(USDRUB.info['bid'], 2)
# datenow = pd.to_datetime('today').strftime('%Y-%m-%d')
# datebefore = (pd.to_datetime('today') - pd.Timedelta('60D')).strftime('%Y-%m-%d')
# dfUSDRUB = yf.download("RUB=X", start=datebefore, end=datenow, interval='1d')
#dfUSDRUB = USDRUB.history(period='2mo', interval='1d')





transient_val_dollar = 0.0
transient_val_euro = 0.1

def daily_routine(context):
    #while True:
        # 86400 sec in day
    #sleep(86400)
    USD = yf.Ticker("RUB=X")
    EUR = yf.Ticker("EURRUB=X")
    dfUSD = USD.history(period='2mo', interval='1d')
    dfEUR = EUR.history(period='2mo', interval='1d')
    draw_pic(dfUSD, 'dol')
    draw_pic(dfEUR, 'eur')

def show_dollar(context):
    global transient_val_dollar
    USD = yf.Ticker("RUB=X")
    priceNow = USD.info['bid']
    transient_val_dollar = priceNow
    #print('show_dollar')
    return priceNow

def show_euro(context):
    global transient_val_euro
    EUR = yf.Ticker("EURRUB=X")
    priceNow = EUR.info['bid']
    transient_val_euro = priceNow
    return priceNow

def signal_message_dollar(context):
    context.bot.send_message(chat_id=context.job.context, text='')

def signal_message_euro(context):
    context.bot.send_message(chat_id=context.job.context, text='')
"""
def signal_routine(dispatcher):
    if not isinstance(dispatcher, Dispatcher):
        raise TypeError('{} should be Dispatcher object'.format(dispatcher))
    while True:
        sleep(60)
        priceEurNow = show_euro()
        priceDolNow = show_dollar()
        for x in ['dol', 'eur']:
            user_data = dispatcher.user_data[x]
            if user_data is None:
                continue
            else:
                if x == 'dol':
                    if show_dollar() > user_data:
                        dispatcher.job_queue.run(signal_message_dollar)
                if x == 'eur':
                    dispatcher.job_queue.run(signal_message_euro)
"""
"""
def signal_routine(context):
    #10:00:00 — 22:00:00
    dp = context.job.context
    curList = ['dol', 'eur']
    _trig_less = False
    _trig_more = False
    for x in curList:
        signalVal = dp.user_data[x]
        if signalVal is None:
            continue
        elif x == 'dol':
            if show_dollar() > signalVal:
                if _trig_less:
                    context.bot.send_message(chat_id=dp.user_data['chat_id'],
                                             text='Обратите внимание на курс доллара!\n'
                                                    'Ваш сигнал {}'.format(signalVal))
                    pass
                _trig_less = False
                _trig_more = True
            if show_dollar() < signalVal:
                if _trig_more:
                    context.bot.send_message(chat_id=dp.user_data['chat_id'],
                                             text='Обратите внимание на курс доллара!\n'
                                                    'Ваш сигнал {}'.format(signalVal))
                _trig_less = True
                _trig_more = False
        elif x == 'eur':
            if show_dollar() > signalVal:
                if _trig_less:
                    context.bot.send_message(chat_id=dp.user_data['chat_id'],
                                             text='Обратите внимание на курс евро!\n'
                                                  'Ваш сигнал {}'.format(signalVal))
                    pass
                _trig_less = False
                _trig_more = True
            if show_dollar() < signalVal:
                if _trig_more:
                    context.bot.send_message(chat_id=dp.user_data['chat_id'],
                                             text='Обратите внимание на курс евро!\n'
                                                  'Ваш сигнал {}'.format(signalVal))
                _trig_less = True
                _trig_more = False
"""


def signal_routine_dollar(context):
    #10:00:00 — 22:00:00
    jc = context.job.context
    _trig_less = jc['queue_dol'].get()
    _trig_more = jc['queue_dol'].get()
    showDollar = transient_val_dollar
    #print(showDollar)
    if showDollar > float(jc['dol']):
        if _trig_less:
            context.bot.send_message(chat_id=jc['chat_id'],
                                     text='Обратите внимание на курс доллара!\n'
                                            'Ваш сигнал {}'.format(jc['dol']))
        _trig_less = False
        _trig_more = True
    if showDollar < float(jc['dol']):
        if _trig_more:
            context.bot.send_message(chat_id=jc['chat_id'],
                                     text='Обратите внимание на курс доллара!\n'
                                            'Ваш сигнал {}'.format(jc['dol']))
        _trig_less = True
        _trig_more = False
    jc['queue_dol'].put(_trig_less)
    jc['queue_dol'].put(_trig_more)

def signal_routine_euro(context):
    #10:00:00 — 22:00:00
    jc = context.job.context
    _trig_less = jc['queue_eur'].get()
    _trig_more = jc['queue_eur'].get()
    showEuro = transient_val_euro
    #print(showEuro)
    if showEuro > float(jc['eur']):
        if _trig_less:
            context.bot.send_message(chat_id=jc['chat_id'],
                                     text='Обратите внимание на курс евро!\n'
                                            'Ваш сигнал {}'.format(jc['eur']))
        _trig_less = False
        _trig_more = True
    if showEuro < float(jc['eur']):
        if _trig_more:
            context.bot.send_message(chat_id=jc['chat_id'],
                                     text='Обратите внимание на курс евро!\n'
                                            'Ваш сигнал {}'.format(jc['eur']))
        _trig_less = True
        _trig_more = False
    jc['queue_eur'].put(_trig_less)
    jc['queue_eur'].put(_trig_more)

def draw_pic(dataframe, currency):
    # check types
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError('{} should be Pandas.DataFrame object'.format(dataframe))
    if not (currency == 'dol') | (currency == 'eur'):
        raise NameError('{} should be \'dol\' or \'eur\''.format(currency))

    fig, ax = plt.subplots(figsize=(10, 7))

    mean_val = dataframe.loc[:, ['High', 'Low']].mean(axis=1)
    x_values = dataframe.index.strftime('%b %d')

    ax.fill_between(x_values, dataframe['High'], dataframe['Low'], color='Purple', alpha=0.2)
    ax.plot(x_values, mean_val, linewidth=2, color='Purple')

    ax.tick_params(axis='x', direction='out', length=8)
    ax.xaxis.set_major_locator(MultipleLocator(4))
    ax.yaxis.set_major_locator(AutoLocator())
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.grid(which='both')
    for tick in ax.get_xticklabels():
        tick.set_rotation(45)
    if currency == 'dol':
        ax.set_title('USD/RUB', fontsize=16, pad=25)
        ax.set_ylabel('RUB per USD')
        fig.savefig('picDol.png')
    if currency == 'eur':
        ax.set_title('EUR/RUB', fontsize=16, pad=25)
        ax.set_ylabel('RUB per EUR')
        fig.savefig('picEur.png')
