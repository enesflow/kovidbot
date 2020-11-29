import telebot
from telebot import types
import time
import requests
import json
import datetime
from threading import Thread
import math
from bs4 import BeautifulSoup
import pyshorteners

shortener = pyshorteners.Shortener()

TOKEN = "1347961551:AAELXJVajybRigjjXcZvqR-LGOrWC9t1zeE"
bot = telebot.TeleBot(TOKEN)

url = 'https://covid19.saglik.gov.tr/TR-66935/genel-koronavirus-tablosu.html'

admin = 1155586242
people = [1155586242, 1221177293, 1011787005]

t = 5
delay = {18: t * 10, 19: t * 5, 20: t * 2, 21: t, 100: 1000}
delayfor = None

today = datetime.date.today()


def format(number):
    res = ''
    j = 0
    for i in str(number)[::-1]:
        res += i
        j += 1
        if j % 3 == 0 and len(str(number)) - j != 0:
            res += ','
    return res[::-1]


def gethtml(url, timeout=5, rplc=""):
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        cont = str(soup.findAll('script')
                   [-1])[67:].replace('</script>', '').replace(';//]]>', '')
    except Exception as e:
        bot.send_message(admin, e)
        return [0]
    return json.loads(str(cont))


api = [69]
checked = False
message = None
covid_data = None


def getcovid():
    global checked
    global delayfor
    global api
    global message
    global covid_data
    try:
        now = False
        print('checking')

        temp = gethtml(url)[0]

        case = int(temp['gunluk_hasta'].replace('.', ''))
        if temp['gunluk_vaka']:
            case += int(temp['gunluk_vaka'].replace('.', ''))
        covid_data = {

            'test': format(temp['gunluk_test'].replace('.', '')),
            'vaka': format(case),
            'vefat': format(temp['gunluk_vefat'].replace('.', '')),
            'iyilesen': format(temp['gunluk_iyilesen'].replace('.', '')),
            'tarih': temp['tarih']

        }
        message = f'''📅 Tarih {covid_data['tarih']}


😷 Test sayısı: {covid_data['test']}
🤒 Vaka sayısı: {covid_data['vaka']}
💀 Vefat sayısı: {covid_data['vefat']}
💉 İyileşen sayısı: {covid_data['iyilesen']}
                    '''

        # print(temp['tarih'])

        d = datetime.datetime.today().strftime("%d.%m.%Y")
        # d = '28.11.2020'
        if d != covid_data['tarih']:
            checked = False

        else:
            if not checked:
                print('now')
                now = True
                checked = True

                print(covid_data)

        print("Checked")
        return [now, message, covid_data]
    except Exception as e:
        print(e)
        return [False, 'Error', covid_data]


def corona():
    while True:

        c = getcovid()
        if c[0]:
            for i in people:
                bot.send_message(i, '🦠')
                bot.send_message(
                    i, 'Hey! Günlük Kovid 19 Tablosu Açıklandı\n' + c[1])

        delayfor = delay[100]
        for i in delay:
            try:
                if int(datetime.datetime.utcnow().hour + 3) >= int(i):
                    delayfor = delay[i]
                if checked == True:
                    delayfor = delay[100]
            except Exception as e:
                print(e)
                delayfor = delay[100]
                bot.send_message(admin, e)

        print(delayfor)
        time.sleep(delayfor)

#
# Get curve
#


def curve(get='gunluk_vaka', h=15, w=8):
    h = h  # - 1

    api_data = gethtml(url)[::-1]
    all_active = []
    if get == 'gunluk_vaka':
        for i in api_data:
            case = (i['gunluk_hasta'].replace('.', ''))
            if not case:
                case = 0
            else:
                case = int(case)
            if i['gunluk_vaka']:
                case += int(i['gunluk_vaka'].replace('.', ''))

            all_active.append(case)

    else:
        for i in api_data:

            if i[get]:
                all_active.append(int(i[get].replace('.', '')))
            else:
                all_active.append(0)

    big_round = math.ceil(len(all_active) / h)
    split_active = split(all_active, value=big_round)
    av_active = []
    for i in split_active:
        # print(i)
        av_active.append(int(sum(i) / len(i)))
    case_round = max(av_active) / w
    for i in range(len(av_active)):
        av_active[i] = math.ceil(av_active[i] / case_round)
    return av_active


def split(arr, value=3):
    arrs = []
    for i in range(0, len(arr), value):
        arrs.append(arr[i:i + value])
    return arrs


@ bot.message_handler(commands=["start"])
def start(message):
    try:
        bot.reply_to(message, "Hello There")
    except Exception as e:
        bot.send_message(
            message.chat.id, 'Bir sorunla karşılaşıldı\n' + str(e))


@ bot.message_handler(commands=["delay"])
def start(message):
    try:
        bot.reply_to(message, str(delayfor))
    except Exception as e:
        bot.send_message(
            message.chat.id, 'Bir sorunla karşılaşıldı\n' + str(e))


@ bot.message_handler(commands=["chatid"])
def chatid(message):
    try:
        bot.reply_to(message, f"Your chat id is {message.chat.id}")
    except Exception as e:
        bot.send_message(
            message.chat.id, 'Bir sorunla karşılaşıldı\n' + str(e))


@ bot.message_handler(commands=["covid"])
def covid(message):
    try:
        bot.send_message(message.chat.id, 'Grafiğiniz hazırlanılıyor')
        h = 20
        w = 8
        d = '_'
        get = 'gunluk_vaka'
        gets = [
            'gunluk_vaka',
            'gunluk_test',
            'gunluk_iyilesen',
            'gunluk_vefat'
        ]
        none = ['_', '-']
        if len(message.text.split()) > 1:
            if message.text.split()[1] in none:
                pass
            else:
                if message.text.split()[1]:
                    try:
                        if get in gets:
                            get = 'gunluk_' + message.text.split()[1]
                        else:
                            bot.send_message(
                                message.chat.id, 'Bilinmeyen değişken ' + str(message.text.split()[1]))
                            return

                    except Exception as e:
                        bot.send_message(
                            message.chat.id, 'Bir sorunla karşılaştık. Lütfen bir daha deneyin\n' + str(e))
                        return
            if len(message.text.split()) > 2:
                if message.text.split()[2] in none:
                    pass
                else:
                    h = int(message.text.split()[2])
                if len(message.text.split()) > 3:
                    if message.text.split()[3] in none:
                        pass
                    else:
                        w = int(message.text.split()[3])

        temp_curve = curve(get=get, h=h, w=w)
        mojis = ['🟩', '🟨', '🟧', '🟥']
        res = ''
        for i in temp_curve:
            j = 2 if i < 0 else i
            res += (
                f"{math.ceil(j) * mojis[math.floor(i / (max(temp_curve) / (len(mojis) - 1)))]}\n")

        bot.send_message(message.chat.id, res)
    except Exception as e:
        bot.send_message(
            message.chat.id, 'Bir sorunla karşılaşıldı\n' + str(e))


@ bot.message_handler(commands=["giris"])
def giris(message):
    try:
        if message.chat.id in people:
            bot.send_message(message.chat.id, "👎🏻")
            bot.send_message(
                message.chat.id, "Zaten listede adınız bulunmakta")
        else:
            people.append(message.chat.id)
            bot.send_message(message.chat.id, "👌🏻")
            bot.send_message(message.chat.id, "Giriş başarıyla tamamlandı")
    except Exception as e:
        bot.send_message(
            message.chat.id, 'Bir sorunla karşılaşıldı\n' + str(e))


@ bot.message_handler(commands=["cikis"])
def cikis(message):
    try:
        if message.chat.id in people:
            people.remove(message. chat.id)
            bot.send_message(message.chat.id, "👌🏻")
            bot.send_message(message.chat.id, "Çıkış başarıyla tamamlandı")
        else:
            bot.send_message(message.chat.id, "👎🏻")
            bot.send_message(
                message.chat.id, "Zaten listede adınız bulunmamakta")
    except Exception as e:
        bot.send_message(
            message.chat.id, 'Bir sorunla karşılaşıldı\n' + str(e))


@ bot.message_handler(commands=["list"])
def lst(message):
    try:
        bot.reply_to(message, str(people))
    except Exception as e:
        bot.send_message(
            message.chat.id, 'Bir sorunla karşılaşıldı\n' + str(e))


@bot.inline_handler(lambda query: query.query == 'tablo')
def tablo(inline_query):
    try:
        temp = getcovid()
        r = types.InlineQueryResultArticle(
            '1',
            '📅 ' + temp[2]['tarih'] + ' 📅',
            types.InputTextMessageContent(
                temp[2]['tarih'] + ' Tarihi için kovid 19 tablosu: \n\n' + temp[1] + '\n\nKovid 19 hakkında günlük bilgi almak için @kovidbot')
        )

        bot.answer_inline_query(inline_query.id, [r])
    except Exception as e:
        print(e)


@bot.inline_handler(lambda query: query.query == 'haber')
def tablo(inline_query):
    try:
        url = ('http://newsapi.org/v2/top-headlines?'
               'q=Koronavirüs&'
               'country=tr&'
               'apiKey=96e467029c384c26a9a57424450cbef5')
        response = requests.get(url)
        news = {'news': response.json()['articles']}
        sorted_obj = news

        sorted_obj['news'] = sorted(
            news['news'], key=lambda x: x['publishedAt'], reverse=True)

        r = []
        j = 0
        for i in sorted_obj['news']:
            j += 1
            r.append(types.InlineQueryResultPhoto(
                str(j),
                i['urlToImage'],
                i['urlToImage'],
                title=i['title'].strip(),

                input_message_content=types.InputTextMessageContent(
                    f'''{i['title'].strip()}
                    
{i['description'].strip()}


Haberin tamamını okumak için hemen tıklayın: {shortener.tinyurl.short(i['url'].strip())}'''
                )
            ))
        bot.answer_inline_query(inline_query.id, r, cache_time=1)
    except Exception as e:
        print(e)


def poll():
    while True:
        try:
            bot.polling(True)
        except Exception as e:
            print(e)
            time.sleep(5)


Thread(target=poll).start()
Thread(target=corona).start()
