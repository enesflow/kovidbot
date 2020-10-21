# -*- coding: utf-8 -*-
import datetime
import time
import json

import requests
import urllib
from pathlib import Path

token = "1232041033:AAHLLOUxgSIgDT4q5qxoZznvM2YvI9wfoXQ"
url = "https://api.telegram.org/bot" + token + "/"
prefix = ""


def getfile(file):  # Get the absolute path of a file
    # stackoverflow stuff
    script_location = Path(__file__).absolute().parent
    file_location = script_location / file
    return file_location


# Get chat id function
def get_chat_id(update):
    chat_id = update["message"]["chat"]["id"]
    return chat_id


# Get message text function
def get_message_text(update):
    message_text = update["message"]["text"]
    return message_text


# Get username function
def get_username(update):
    user_name = update["message"]["chat"]["first_name"] + " " + update["message"]["chat"]["last_name"]
    return user_name


# Get last update function
def last_update(req):
    response = requests.get(req + "getUpdates")
    response = response.json()
    result = response["result"]
    total_updates = len(result) - 1
    return result[total_updates]  # Get the last message


# Send message function
def send_message(chat_id, message_text):
    params = {"chat_id": chat_id, "text": message_text}
    response = requests.post(url + "sendMessage", data=params)
    return response


def command(message, command):
    if message.lower() == prefix + command:
        return True
    return False


def getlist():
    with open(getfile("people.txt"), "r") as f:
        temp = eval(f.read())
        return temp


def append(w):
    lst = getlist()
    with open(getfile("people.txt"), "w") as f:
        lst.append(w)
        f.write(str(lst))


def remove(w):
    lst = getlist()
    with open(getfile("people.txt"), "w") as f:
        lst.remove(w)
        f.write(str(lst))


# Main function
def main():
    update_id = last_update(url)["update_id"]
    while True:
        update = last_update(url)
        if update_id == update["update_id"]:
            print(get_message_text(update))
            if command(get_message_text(update), "kayit"):
                print("kayit")
                if get_chat_id(update) in getlist():
                    send_message(get_chat_id(update), "Zaten adınız kayıt listesinde var")
                else:
                    append(get_chat_id(update))
                    send_message(get_chat_id(update),
                                 f"""Hey {get_username(update)}! Kaydınız başarıyla oluşturuldu.\n
Kovid19 tablosu açıklandığında size haber vereceğim!"""
                                 )
            if command(get_message_text(update), "cikis"):
                print("cikis")
                if get_chat_id(update) in getlist():
                    remove(get_chat_id(update))
                    send_message(get_chat_id(update), "Kaydınız başarıyla silindi!")
                else:
                    send_message(get_chat_id(update), "Zaten kayıt listesinde değilsiniz")
            if command(get_message_text(update), "people"):
                print("people")
                send_message(get_chat_id(update), str(getlist()))


            update_id += 1
        checkcorona()
        time.sleep(0.1)


def gethtml(url):
    thesite = urllib.request.urlopen(url).read()
    return thesite.decode("utf8")


















def checkcorona():
    URL = "https://covid19.saglik.gov.tr/covid19api?getir=sondurum"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4257.0 Safari/537.36"
    }
    newDay = False
    date = "Whatever"

    html = gethtml(URL)

    if date != datetime.datetime.today().strftime("%d.%m.%Y"):
        newDay = False

    dicthtml = json.loads(html)[0]

    now = datetime.datetime.now()

    date = datetime.datetime.today().strftime("%d.%m.%Y")
    hour = now.hour
    if str(dicthtml["tarih"]) == str(date):
        if not (newDay):
            message = (
                f'''Tarih: 📅 {date} 📅\n
Merhabalar,\n\n
🤖Günlük 🦠koronavirüs🦠 tablosu açıklandı\n
😷Test sayısı:    {str(dicthtml["gunluk_test"]).replace(".", "")}
🤒Vaka sayısı:   {str(dicthtml["gunluk_vaka"]).replace(".", "")}
💀Vefat sayısı:   {str(dicthtml["gunluk_vefat"]).replace(".", "")}
💉İyileşen sayısı:   {str(dicthtml["gunluk_iyilesen"]).replace(".", "")} \n\n
Saygılarımla'''
            )
            print("NOW")
            newDay = True
            for person in getlist():
                send_message(person, message)
            print("Now")
    else:
        print("Not now")


main()
