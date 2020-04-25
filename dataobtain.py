import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns

USDRUB = yf.Ticker("RUB=X")
priceNow = round(USDRUB.info['bid'], 2)
#datenow = pd.to_datetime('today').strftime('%Y-%m-%d')
#datebefore = (pd.to_datetime('today') - pd.Timedelta('60D')).strftime('%Y-%m-%d')
#dfUSDRUB = yf.download("RUB=X", start=datebefore, end=datenow, interval='1d')
dfUSDRUB = USDRUB.history(period='2mo', interval='1d')

def draw_pic(dataframe):
    sns.set()
    plt.figure(figsize=(10,7))
    plt.title('USD/RUB', fontsize=16, pad=30)
    plt.ylabel('RUB per USD')
    plt.xticks(rotation=45)
    plt.plot(dataframe['Open'], linewidth=2, color='Purple')
    plt.savefig('pic.png')

