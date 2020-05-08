import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator, AutoLocator
import pandas as pd

"""
Global values for storing dollar and euro values. Updates every 20 sec in separate threads
If user set up signal, it produces another monitoring thread in signal_routine_dollar and 
signal_routine_euro where this global values used. Maybe it's not the best practice to use global val 
for storing information between threads... 
"""

transient_val_dollar = 0.0
transient_val_euro = 0.0

def daily_routine(context):
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
    # transient_val_dollar = priceNow
    return priceNow

def show_euro(context):
    global transient_val_euro
    EUR = yf.Ticker("EURRUB=X")
    priceNow = EUR.info['bid']
    # transient_val_euro = priceNow
    return priceNow
"""
def signal_message_dollar(context):
    context.bot.send_message(chat_id=context.job.context, text='')

def signal_message_euro(context):
    context.bot.send_message(chat_id=context.job.context, text='')
"""


def signal_routine_dollar(context):
    #10:00:00 — 22:00:00
    jc = context.job.context['dol_data']
    user_ids = jc.keys()
    showDollar = show_dollar(context)
    for id_ in user_ids:
        if id_ is None:
            continue
        _trig_less = jc[id_]['trig_less']
        _trig_more = jc[id_]['trig_more']
        if showDollar > jc[id_]['val']:
            if _trig_less:
                context.bot.send_message(chat_id=id_,
                                         text='Обратите внимание на курс доллара!\n'
                                                'Ваш сигнал {}'.format(jc[id_]['val']))
            _trig_less = False
            _trig_more = True
        if showDollar < jc[id_]['val']:
            if _trig_more:
                context.bot.send_message(chat_id=id_,
                                         text='Обратите внимание на курс доллара!\n'
                                                'Ваш сигнал {}'.format(jc[id_]['val']))
            _trig_less = True
            _trig_more = False
        jc[id_]['trig_less'] = _trig_less
        jc[id_]['trig_more'] = _trig_more


def signal_routine_euro(context):
    #10:00:00 — 22:00:00
    jc = context.job.context['eur_data']
    user_ids = jc.keys()
    showEuro = show_euro(context)
    for id_ in user_ids:
        if id_ is None:
            continue
        _trig_less = jc[id_]['trig_less']
        _trig_more = jc[id_]['trig_more']
        if showEuro > jc[id_]['val']:
            if _trig_less:
                context.bot.send_message(chat_id=id_,
                                         text='Обратите внимание на курс евро!\n'
                                                'Ваш сигнал {}'.format(jc[id_]['val']))
            _trig_less = False
            _trig_more = True
        if showEuro < jc[id_]['val']:
            if _trig_more:
                context.bot.send_message(chat_id=id_,
                                         text='Обратите внимание на курс евро!\n'
                                                'Ваш сигнал {}'.format(jc[id_]['val']))
            _trig_less = True
            _trig_more = False
        jc[id_]['trig_less'] = _trig_less
        jc[id_]['trig_more'] = _trig_more

def draw_pic(dataframe, currency):
    # check types
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError('{} should be Pandas.DataFrame object'.format(dataframe))
    if not (currency == 'dol') | (currency == 'eur'):
        raise NameError('{} should be \'dol\' or \'eur\''.format(currency))

    # Draw pic
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
