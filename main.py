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
    try:
        thesite = urllib.request.urlopen(url, timeout=timeout).read()
    except:
        return -1
    return json.loads(thesite.decode('utf8').replace(rplc, ""))


api = [69]

checked = False


def corona():
    global today
    global delayfor
    global api
    while True:
        try:
            print("Checking")
            temp = gethtml(url)
            if str(datetime.date.today()) not in temp[-1]['Date']:
                checked = False
            if not checked and str(datetime.date.today()) in temp[-1]['Date']:
                print("Now")

                for person in people:
                    bot.send_message(person, "🦠")
                    bot.send_message(
                        person,
                        f'Tarih {today}\n\n😷 Vaka\t{list(api)[-1]["Confirmed"] - list(api)[-2]["Confirmed"]}\n☠ Vefat\t{list(api)[-1]["Deaths"] - list(api)[-2]["Deaths"]}\n😁 İyileşen\t{list(api)[-1]["Recovered"] - list(api)[-2]["Recovered"]}'
                    )
                checked = True

            else:
                print("Not now")

            print("Checked")
            delayfor = delay[100]
            for i in delay:
                try:
                    if int(datetime.datetime.now().hour) >= int(i):
                        delayfor = delay[i]
                except Exception as e:
                    print(e)
                    delayfor = delay[100]
                    bot.send_message(admin, e)

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
    if get.lower() == 'new':
        api_data.insert(0, {'Confirmed': 0})
        temp = api_data[0]
        for i in api_data[1:]:
            # - api_data[i-1]['Active'])
            all_active.append((i['Confirmed'] - temp['Confirmed']))
            temp = i
    else:
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
    from pprint import pprint
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
            'active': 'Active cases',
            'deaths': 'Deaths',
            'confirmed': 'Total cases',
            'recovered': 'Recovered',
            'new': 'New cases'
        }
        none = ['_', '-']
        if len(message.text.split()) > 1:
            if message.text.split()[1] in none:
                pass
            else:
                if message.text.split()[1]:
                    try:
                        temp = str(translator.translate(
                            str(message.text.split()[1]), dest='en').text)
                        if temp in gets:
                            get = temp
                        else:
                            bot.send_message(
                                message.chat.id, 'Bilinmeyen değişken ' + str(message.text.split()[1]) + ' veya ' + translator.translate(message.text.split()[1], dest='en').text.capitalize())
                            return

                    except:
                        bot.send_message(
                            message.chat.id, 'Bir sorunla karşılaştık. Lütfen bir daha deneyin')
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

        temp_curve = curve(get=get.capitalize(), h=h, w=w, c=c)
        mojis = ['🟩', '🟨', '🟧', '🟥']
        res = ''
        for i in temp_curve:
            j = 2 if i < 0 else i
            res += (
                f"{math.ceil(j) * mojis[math.floor(i / (max(temp_curve) / (len(mojis) - 1)))]}\n")

        bot.send_message(
            message.chat.id, f'''{translator.translate(c, dest='tr').text.capitalize()} ülkesisin {translator.translate(gets[get.lower()], dest='tr').text} grafiği''')
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
