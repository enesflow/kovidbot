import datetime
import json
import urllib

import requests
import time

url = "https://api.telegram.org/bot1338035537:AAFECSSQgKYcroddrdK8aS5W1QE_UiXnxOM/"
prefix = ""

people = []

newDay = True

URL = "https://covid19.saglik.gov.tr/covid19api?getir=sondurum"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4257.0 Safari/537.36"
}

currentdate = "Whatever"
currentsec = "-1"

maxtime = 40
a = 1

deftime = 300
timedict = {18:60,19:30,20:15,21:9}

def get_delay(h):
    tempd = deftime
    for t, d in timedict.items():
        if t < h < t + 2:
            tempd = d
    return tempd

# Get chat id function
def get_chat_id(update):
    chat_id = update["message"]["chat"]["id"]
    return chat_id


# Get message text function
def get_message_text(update):
    message_text = update["message"]["text"]
    return message_text


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


def gethtml(url, timeout):
    thesite = urllib.request.urlopen(url, timeout=timeout).read()
    return thesite.decode("utf8")


# Main function
def main():
    update_id = last_update(url)["update_id"]
    while True:
        update = last_update(url)
        if update_id == update["update_id"]:
            current_chat = get_chat_id(update)
            current_message = get_message_text(update)
            if command(current_message, "bot"):
                send_message(current_chat, "Merhaba! Ben Biber Bot")
            if command(current_message, "covid"):
                if not current_chat in people:
                    people.append(current_chat)
                    send_message(current_chat, "Kaydınız başarıyla tamamlandı!")
                else:
                    send_message(current_chat, "Zaten adınız listede mevcut")
            if command(current_message, "dur"):
                if current_chat in people:
                    people.remove(current_chat)
                    send_message(current_chat, "Kaydınız başarıyla kaldırıldı!")
                else:
                    send_message(current_chat, "Zaten adınız listede bulunmamakta")
            if command(current_message, "people"):
                send_message(current_chat, str(people))

            update_id += 1
        checkedcovid = checkcorona()
        if (checkedcovid[0]):
            for person in people:
                send_message(person, checkedcovid[1])
        # time.sleep(0.05)





def checkcorona():
    global currentsec
    global currentdate
    global newDay

    everysecs = get_delay(int(datetime.datetime.today().strftime("%H")))
    print(everysecs)
    if currentdate != datetime.datetime.today().strftime("%d.%m.%Y"):
        newDay = True

    if newDay:
        # print(currentsec, datetime.datetime.today().strftime("%S"))
        diff = int(datetime.datetime.today().strftime("%S")) - int(currentsec)
        if diff >= everysecs or diff < 0:
            print("checking")
            currentsec = datetime.datetime.today().strftime("%S")
            html = gethtml(URL, 10)

            dicthtml = json.loads(html)[0]


            date = datetime.datetime.today().strftime("%d.%m.%Y")
            if str(dicthtml["tarih"]) == str(date):
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
                newDay = False
                return [True, message]
            print("checked")

    return [False]




main()
