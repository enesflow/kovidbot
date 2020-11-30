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
import pymongo
from pymongo import MongoClient

# Url Shortener
shortener = pyshorteners.Shortener()

# Bot
TOKEN = "1347961551:AAELXJVajybRigjjXcZvqR-LGOrWC9t1zeE"
bot = telebot.TeleBot(TOKEN)

# Covid URL
url = 'https://covid19.saglik.gov.tr/TR-66935/genel-koronavirus-tablosu.html'

# Default People
admin = 1155586242
people = {1155586242: 'Enes', 1221177293: 'Süreyya', 1011787005: 'İbrahim'}

# Get mongodb password
with open('mongo.txt', 'r') as f:
    lines = f.readlines()
    mongopassword = lines[0]

# Mongodb stuff
cluster = MongoClient(
    f'mongodb+srv://admin:{mongopassword}@kovidbot.ksmsj.mongodb.net/kovidbot?retryWrites=true&w=majority')
db = cluster['kovid']
collection = db['people']

# Insert default people
print('adding people')
for i in people:
    try:
        collection.insert_one({'_id': i, 'name': people[i]})
    except Exception as e:
        if 'duplicate key error collection' in str(e):
            pass
        else:
            bot.send_message(admin, 'Error ' + str(e))


print('Done')

# Time
t = 5
delay = {18: t * 10, 19: t * 5, 20: t * 2, 21: t, 100: 1000}
delayfor = None


# A basic send message function to use multithreading
def send_to(chat, messages):
    for i in messages:
        bot.send_message(chat, i)


# Function to format a number like 123456 -> 123,456
def format(number):
    res = ''
    j = 0
    for i in str(number)[::-1]:
        res += i
        j += 1
        if j % 3 == 0 and len(str(number)) - j != 0:
            res += ','
    return res[::-1]

# Function to convert our database into an array


def getdb():
    temp = []
    for i in collection.find({}):
        temp.append(i)
    return temp

# A function to get the covid table from the covid url


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


# Some variables for getcovid()
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

        # Get the covid table
        temp = gethtml(url)[0]

        # Get infected people
        case = int(temp['gunluk_hasta'].replace('.', ''))
        if temp['gunluk_vaka']:
            case += int(temp['gunluk_vaka'].replace('.', ''))

        # Make a dictionary for easier use
        covid_data = {

            'test': format(temp['gunluk_test'].replace('.', '')),
            'vaka': format(case),
            'vefat': format(temp['gunluk_vefat'].replace('.', '')),
            'iyilesen': format(temp['gunluk_iyilesen'].replace('.', '')),
            'tarih': temp['tarih']

        }

        # Set message
        message = f'''📅 Tarih {covid_data['tarih']}

😷 Test sayısı: {covid_data['test']}
🤒 Vaka sayısı: {covid_data['vaka']}
💀 Vefat sayısı: {covid_data['vefat']}
💉 İyileşen sayısı: {covid_data['iyilesen']}
                    '''

        # Check if the day has passed
        d = datetime.datetime.today().strftime("%d.%m.%Y")
        if d != covid_data['tarih']:
            checked = False

        # If not
        else:
            # Check if we already checked
            if not checked:
                # If not mark as checked
                print('now')
                now = True
                checked = True

                print(covid_data)

        print("Checked")
        # Return
        return [now, message, covid_data]
    except Exception as e:
        print(e)
        return [False, 'Error', covid_data]


def corona():
    while True:

        # Get covid data
        c = getcovid()
        # If today is the day
        if c[0]:
            # Get all the people from mongodb
            temp = getdb()

            # Send messages to these people using multithreading
            for i in temp:
                Thread(target=send_to, args=[i['_id'], [
                       '🦠', f'Hey {i["name"]}! Günlük Kovid 19 Tablosu Açıklandı\n{c[1]}']]).start()

        # Delay
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

# Get curve


def curve(get='gunluk_vaka', h=15, w=8):
    # Split function to split an array into smaller arrays for rounding up the data
    def split(arr, value=3):
        arrs = []
        for i in range(0, len(arr), value):
            arrs.append(arr[i:i + value])
        return arrs

    # Get the whole table
    api_data = gethtml(url)[::-1]
    all_active = []

    # If we want the infected people add vaka and hasta together
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

    # If not
    else:
        # Get that data
        for i in api_data:

            if i[get]:
                all_active.append(int(i[get].replace('.', '')))
            else:
                all_active.append(0)

    # Round the data
    big_round = math.ceil(len(all_active) / h)
    split_active = split(all_active, value=big_round)
    av_active = []
    for i in split_active:
        av_active.append(int(sum(i) / len(i)))
    case_round = max(av_active) / w
    for i in range(len(av_active)):
        av_active[i] = math.ceil(av_active[i] / case_round)

    # Return
    return av_active


# Start command
@ bot.message_handler(commands=["start"])
def start(message):
    try:
        bot.reply_to(message, "Hello There")
    except Exception as e:
        bot.send_message(
            message.chat.id, 'Bir sorunla karşılaşıldı\n' + str(e))

# Command to get chat id


@ bot.message_handler(commands=["chatid"])
def chatid(message):
    try:
        bot.reply_to(message, f"Your chat id is {message.chat.id}")
    except Exception as e:
        bot.send_message(
            message.chat.id, 'Bir sorunla karşılaşıldı\n' + str(e))

# Command to get curve


@ bot.message_handler(commands=["covid"])
def covid(message):
    try:
        bot.send_message(message.chat.id, 'Grafiğiniz hazırlanılıyor')
        h = 20  # height
        w = 8  # width
        get = 'gunluk_vaka'  # Thing to get
        gets = [
            'gunluk_vaka',
            'gunluk_test',
            'gunluk_iyilesen',
            'gunluk_vefat'
        ]  # All avaible things to get
        # The user will put one of these if he/she wants the default value
        none = ['_', '-']
        # If the user specified the thing to get
        if len(message.text.split()) > 1:
            if message.text.split()[1] in none:
                pass
            else:
                if message.text.split()[1]:
                    # Check if it is avaible
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

            # If the user also specified the height
            if len(message.text.split()) > 2:
                if message.text.split()[2] in none:
                    pass
                else:
                    h = int(message.text.split()[2])
                # If the user also specified the width
                if len(message.text.split()) > 3:
                    if message.text.split()[3] in none:
                        pass
                    else:
                        w = int(message.text.split()[3])

        # Temp value for the curve
        temp_curve = curve(get=get, h=h, w=w)
        # Emojis short -> long
        mojis = ['🟩', '🟨', '🟧', '🟥']
        res = ''
        for i in temp_curve:
            # Do this so the value will not be under 0
            j = 1 if i < 0 else i
            # Some math to calculate which emoji will come and add this to our string
            res += (
                f"{math.ceil(j) * mojis[math.floor(i / (max(temp_curve) / (len(mojis) - 1)))]}\n")

        # Send it
        bot.send_message(message.chat.id, res)
    except Exception as e:
        bot.send_message(
            message.chat.id, 'Bir sorunla karşılaşıldı\n' + str(e))

# Command to enter


@ bot.message_handler(commands=["giris"])
def giris(message):
    try:
        bot.send_message(message.chat.id, 'Lütfen biraz bekleyin...')
        # Get all the people in our database
        temp = getdb()
        # Check if the user is already entered
        if message.chat.id in temp:
            bot.send_message(message.chat.id, "👎🏻")
            bot.send_message(
                message.chat.id, "Zaten listede adınız bulunmakta")
        # If not
        else:
            # Insert user to our database
            collection.insert_one(
                {'_id': message.chat.id, 'name': message.from_user.first_name})
            bot.send_message(message.chat.id, "👌🏻")
            bot.send_message(message.chat.id, "Giriş başarıyla tamamlandı")
    except Exception as e:
        bot.send_message(
            message.chat.id, 'Bir sorunla karşılaşıldı\n' + str(e))

# Command to leave


@ bot.message_handler(commands=["cikis"])
def cikis(message):
    try:
        bot.send_message(message.chat.id, 'Lütfen biraz bekleyin...')
        # Get all the people in our database
        temp = getdb()
        # Check if the user is in our database
        if message.chat.id in temp:
            # Remove user from our database
            collection.remove(
                {'_id': message.chat.id, 'name': message.from_user.first_name})
            bot.send_message(message.chat.id, "👌🏻")
            bot.send_message(message.chat.id, "Çıkış başarıyla tamamlandı")
        # If not
        else:
            bot.send_message(message.chat.id, "👎🏻")
            bot.send_message(
                message.chat.id, "Zaten listede adınız bulunmamakta")
    except Exception as e:
        bot.send_message(
            message.chat.id, 'Bir sorunla karşılaşıldı\n' + str(e))

# Command to list all the people in our database


@ bot.message_handler(commands=["list"])
def lst(message):
    try:
        bot.send_message(message.chat.id, 'Lütfen biraz bekleyin...')
        # Get the database
        temp = getdb()
        # Prettify it
        p = ''
        for i in temp:
            p += str(i) + '\n'
        # Send
        bot.reply_to(message, p)
    except Exception as e:
        bot.send_message(
            message.chat.id, 'Bir sorunla karşılaşıldı\n' + str(e))

# Inline command to send the latest covid table to someone


@ bot.inline_handler(lambda query: query.query == 'tablo')
def tablo(inline_query):
    try:
        # Get the latest covid table
        temp = getcovid()
        # Make it an inline command
        r = types.InlineQueryResultArticle(
            '1',
            # Title
            '📅 ' + temp[2]['tarih'] + ' 📅',
            # Content
            types.InputTextMessageContent(
                temp[2]['tarih'] + ' Tarihi için kovid 19 tablosu: \n' + temp[1] + '\n\nKovid 19 hakkında günlük bilgi almak için @kovidbot')
        )
        # Answer the inline command
        bot.answer_inline_query(inline_query.id, [r])
    except Exception as e:
        print(e)

# Inline command to get the latest new about covid19


@ bot.inline_handler(lambda query: query.query == 'haber')
def tablo(inline_query):
    try:
        # Api stuff
        url = ('http://newsapi.org/v2/top-headlines?'
               'q=Koronavirüs&'
               'country=tr&'
               'apiKey=96e467029c384c26a9a57424450cbef5')
        response = requests.get(url)
        # News variable
        news = {'news': response.json()['articles']}
        sorted_obj = news

        # Sort the news variable from newest to oldest
        sorted_obj['news'] = sorted(
            news['news'], key=lambda x: x['publishedAt'], reverse=True)

        # Make an array of the news
        r = []
        j = 0
        # Inline command stuff
        for i in sorted_obj['news']:
            j += 1
            # Add photo to inline command
            r.append(types.InlineQueryResultPhoto(
                str(j),  # Index
                i['urlToImage'],  # Url to image
                i['urlToImage'],  # Url to image
                title=i['title'].strip(),  # Title

                # The content of the news
                input_message_content=types.InputTextMessageContent(
                    f'''{i['title'].strip()}

{i['description'].strip()}


Haberin tamamını okumak için hemen tıklayın: {shortener.dagd.short(i['url'].strip())}'''
                )
            ))
        # Answer the inline command
        bot.answer_inline_query(inline_query.id, r, cache_time=1)
    except Exception as e:
        print(e)

# Check for new messages


def poll():
    while True:
        try:
            bot.polling(True)
        except Exception as e:
            print(e)
            time.sleep(5)


# Start threads
Thread(target=poll).start()
Thread(target=corona).start()
