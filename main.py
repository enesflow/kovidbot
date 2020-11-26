import telebot
import time
import urllib
import json
import datetime
from threading import Thread
import math

TOKEN = "1128846573:AAEOPz-8xmOY7dA5iiqFdkS_Gy4MZfOPiwY"
bot = telebot.TeleBot(TOKEN)

url = "https://api.covid19api.com/total/dayone/country/turkey"

admin = 1155586242
people = [1155586242]  # , 1221177293]

delay = {18: 30, 19: 15, 20: 7.5, 21: 5, 200: 100, 400: 100, 100: 100}
delayfor = None


def gethtml(url, timeout=5, rplc=""):
    thesite = urllib.request.urlopen(url, timeout=timeout).read()
    return json.loads(thesite.decode('utf8').replace(rplc, ""))


today = datetime.date.today().strftime("%d.%m.%Y")
newDay = True

moji = "🟥"

api = None


def corona():
    global newDay
    global today
    global delayfor
    global api
    while True:
        try:
            print("Checking")
            temp = gethtml(url)
            if not api or api != temp:
                api = temp
                today = datetime.date.today().strftime("%d.%m.%Y")
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
            delayfor = delay[200]
            for i in delay:
                try:
                    if int(datetime.datetime.now().hour) >= int(i):
                        delayfor = delay[i]
                except Exception as e:
                    delayfor = delay[400]
                    bot.send_message(admin, e)

            if not newDay:
                delayfor = delay[100]
            print(delayfor)
            time.sleep(delayfor)
        except Exception as e:  # Exception as e
            print(e)
            time.sleep(delay[100])
            # bot.send_message(1155586242, f"ERROR\n{e}")


def split(arr, value=3):
    arrs = []
    for i in range(0, len(arr), value):
        arrs.append(arr[i:i + value])
    return arrs


def av(arr):
    return int(sum(arr) / len(arr))


def getcurve(r=5, emoji=moji, sendwhat="gva", m=4):
    rpl = {
        "gva": "gunluk_vaka",
        "gt": "gunluk_test",
        "gve": "gunluk_vefat",
        "gi": "gunluk_iyilesen"
    }
    if sendwhat in rpl:
        what = rpl[sendwhat]
    else:
        return None
    vl = []
    avl = []
    cavl = []
    URL = 'https://covid19.saglik.gov.tr/covid19api?getir=liste'
    covid = reversed(gethtml(URL, rplc="."))

    for i in covid:
        try:
            if what == "gunluk_vefat":
                vl.append(int(int(i[what]) / m))
            elif what == "gunluk_test":
                vl.append(int(int(i[what]) / (m * 750)))
            else:
                vl.append(int(int(i[what]) / (m * 25)))

        except ValueError:
            pass

    vl = split(vl, r)
    for i in vl:
        avl.append(av(i))

    cavl = avl
    avl = []
    for i in cavl:
        avl.append(math.ceil(i / r) * emoji)

    return avl


@ bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "Hello There")


@ bot.message_handler(commands=["delay"])
def start(message):
    bot.reply_to(message, str(delayfor))


@ bot.message_handler(commands=["chatid"])
def chatid(message):
    bot.reply_to(message, f"Your chat id is {message.chat.id}")


@ bot.message_handler(commands=["covid"])
def covid(message):
    bot.send_message(message.chat.id, 'service is temporarily unavaible')
    # if len(message.text.split()) > 1:
    #    val = message.text.split()[1]
    # else:
    #    val = "gva"
    #curve = ""
    #allcurve = getcurve(sendwhat=val)
    # if allcurve:
    #    for i in allcurve:
    #        curve += i + "\n"
    #    bot.send_message(message.chat.id, curve)
    # else:
    #    bot.send_message(message.chat.id, "...")


@ bot.message_handler(commands=["giris"])
def giris(message):
    if message.chat.id in people:
        bot.send_message(message.chat.id, "👎🏻")
        bot.send_message(message.chat.id, "Zaten listede adınız bulunmakta")
    else:
        people.append(message.chat.id)
        bot.send_message(message.chat.id, "👌🏻")
        bot.send_message(message.chat.id, "Giriş başarıyla tamamlandı")


@ bot.message_handler(commands=["cikis"])
def cikis(message):
    if message.chat.id in people:
        people.remove(message.chat.id)
        bot.send_message(message.chat.id, "👌🏻")
        bot.send_message(message.chat.id, "Çıkış başarıyla tamamlandı")
    else:
        bot.send_message(message.chat.id, "👎🏻")
        bot.send_message(message.chat.id, "Zaten listede adınız bulunmamakta")


@ bot.message_handler(commands=["list"])
def lst(message):
    bot.reply_to(message, str(people))


def poll():
    while True:
        try:
            bot.polling()
        except Exception as e:
            print(e)
            time.sleep(5)


Thread(target=poll).start()
Thread(target=corona).start()
