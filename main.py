import telebot
import time
import urllib
import json
import datetime
from threading import Thread
import math
import random
from googletrans import Translator

translator = Translator()

TOKEN = "1128846573:AAEOPz-8xmOY7dA5iiqFdkS_Gy4MZfOPiwY"
bot = telebot.TeleBot(TOKEN)

url = "https://api.covid19api.com/total/dayone/country/turkey"

admin = 1155586242
people = [1155586242, 1221177293]

delay = {18: 30, 19: 15, 20: 7.5, 21: 3, 100: 1000}
delayfor = None

today = datetime.date.today()


def gethtml(url, timeout=5, rplc=""):
    thesite = urllib.request.urlopen(url, timeout=timeout).read()
    return json.loads(thesite.decode('utf8').replace(rplc, ""))


newDay = False

api = [69]


def corona():
    global newDay
    global today
    global delayfor
    global api
    while True:
        try:
            print("Checking")
            temp = gethtml(url)
            if str(datetime.date.today()) in temp[-1]['Date']:
                api = temp
                today = temp[-1]['Date'][:10]
                print(today)
                newDay = True
            if newDay:
                print("Now")
                newDay = False

                for person in people:
                    bot.send_message(person, "🦠")
                    bot.send_message(
                        person,
                        f'Tarih {today}\n\n😷 Vaka\t{list(api)[-1]["Confirmed"] - list(api)[-2]["Confirmed"]}\n☠ Vefat\t{list(api)[-1]["Deaths"] - list(api)[-2]["Deaths"]}\n😁 İyileşen\t{list(api)[-1]["Recovered"] - list(api)[-2]["Recovered"]}'
                    )

            else:
                print("Not now")

            print("Checked")
            delayfor = delay[100]
            for i in delay:
                try:
                    if int(datetime.datetime.now().hour) >= int(i):
                        delayfor = delay[i]
                except Exception as e:
                    delayfor = delay[100]
                    bot.send_message(admin, e)

            if not newDay:
                delayfor = delay[100]
            print(delayfor)
            time.sleep(delayfor)
        except Exception as e:  # Exception as e
            print(e)
            time.sleep(delay[100])
            # bot.send_message(1155586242, f"ERROR\n{e}")

#
# Get curve
#


def curve(get='Active', h=15, w=8, c='turkey'):
    url = "https://api.covid19api.com/total/dayone/country/" + c
    h = h  # - 1

    api_data = gethtml(url)
    all_active = []
    for i in api_data:
        all_active.append(i[get])

    big_round = math.ceil(len(all_active) / h)
    split_active = split(all_active, value=big_round)
    av_active = []
    for i in split_active:
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
        c = 'turkey'
        d = '_'
        get = 'Active'
        gets = {
            'Active': 'Active cases',
            'Deaths': 'Deaths',
            'Confirmed': 'Total cases',
            'Recovered': 'Recovered',
            'Date': 'Date'
        }
        none = ['_', '']
        if len(message.text.split()) > 1:
            if message.text.split()[1] in none:
                pass
            else:
                if translator.translate(message.text.split()[1], dest='en').text.capitalize() in gets:
                    get = translator.translate(
                        message.text.split()[1], dest='en').text.capitalize()
                else:
                    bot.send_message(
                        message.chat.id, 'Bilinmeyen değişken ' + str(message.text.split()[1]) + ' veya ' + translator.translate(message.text.split()[1], dest='en').text.capitalize())
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
                    if len(message.text.split()) > 4:
                        if message.text.split()[4] in none:
                            pass
                        else:
                            c = translator.translate(message.text.split()[
                                                     4], dest='en').text.lower()

        temp_curve = curve(get=get, h=h, w=w, c=c)
        mojis = ['🟩', '🟨', '🟧', '🟥']
        res = ''
        for i in temp_curve:
            res += (
                f"{i * mojis[math.floor(i / (max(temp_curve) / (len(mojis) - 1)))]}\n")

        bot.send_message(
            message.chat.id, f'''{translator.translate(c, dest='tr').text.capitalize()} ülkesisin {translator.translate(gets[get], dest='tr').text} grafiği''')
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
            people.remove(message.chat.id)
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


def poll():
    while True:
        try:
            bot.polling()
        except Exception as e:
            print(e)
            time.sleep(5)


Thread(target=poll).start()
Thread(target=corona).start()
