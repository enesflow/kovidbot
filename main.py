import telebot
from telebot import types
import time
import requests
import json
import datetime
from threading import Thread
import math
import os
from bs4 import BeautifulSoup
import pyshorteners
import pymongo
from pymongo import MongoClient

cache = {
    'tablo': None
}

# Url Shortener
shortener = pyshorteners.Shortener()

# Bot
TOKEN = os.environ['TOKEN']
bot = telebot.TeleBot(TOKEN)

# Covid URL
url = 'https://covid19.saglik.gov.tr/TR-66935/genel-koronavirus-tablosu.html'

# Default People
admin = int(os.environ['ADMIN'])
people = {admin: 'Enes'}


# Mongodb stuff
cluster = MongoClient(os.environ['MONGO'])
db = cluster['kovid']
collection = db['people']


# Time
t = 5
delay = {18: t * 10, 19: t * 5, 20: t * 2, 21: t, 100: 1000}
delayfor = None


# A basic send message function to use multithreading
def send_multiple(chat, messages):
    for i in messages:
        bot.send_message(chat, i)


def send_one(chat, message, mode='Markdown'):
    bot.send_message(chat, message, parse_mode=mode)


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

# A basic function to add to database to use multithreading


def add_db(a):
    try:
        collection.insert_one(a)
    except Exception as e:
        print(e)

# A basic function to delete from database to use multithreading


def del_db(a):
    try:
        collection.delete_many(a)
    except Exception as e:
        print(e)


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


# Insert default people
print('adding people')
for i in people:
    try:
        Thread(target=add_db, args=({'_id': i, 'name': people[i]},)).start()
    except Exception as e:
        if 'duplicate key error collection' in str(e):
            pass
        else:
            bot.send_message(admin, 'Error ' + str(e))


print('Done')

# Some variables for getcovid()
api = [69]
message = None
covid_data = None


def getcovid():
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
            with open('checked.txt', 'w') as f:
                f.write('False')

        # If not
        else:
            # Check if we already checked
            with open('checked.txt', 'r') as f:
                checked = f.readlines()[0]
            if checked == 'False':
                # If not mark as checked
                print('now')
                now = True
                with open('checked.txt', 'w') as f:
                    f.write('True')

        print("Checked")
        # Return
        cache['tablo'] = [now, message, covid_data]
        return [now, message, covid_data]
    except Exception as e:
        print(e)
        return [False, 'Error', covid_data]


def send_curve(id, data):

    temp_curve = curve(get=data['get'], h=data['h'], w=data['w'])
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
    bot.send_message(id, res)


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
                Thread(target=send_multiple, args=[i['_id'], [
                       '🦠', f'Hey {i["name"]}! Günlük Kovid 19 Tablosu Açıklandı\n{c[1]}']]).start()

        # Delay
        delayfor = delay[100]
        for i in delay:
            try:
                if int(datetime.datetime.utcnow().hour + 3) >= int(i):
                    delayfor = delay[i]

                with open('checked.txt', 'r') as f:
                    checked = f.readlines()[0]
                if checked == 'True':
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
        bot.send_message(
            message.chat.id, f"Merhaba {message.from_user.first_name}! Lütfen yardım için /help veya /yardim yazın.")
    except Exception as e:
        bot.send_message(
            message.chat.id, 'Bir sorunla karşılaşıldı\n' + str(e))

# Start command


@ bot.message_handler(commands=["help", "yardim"])
def start(message):
    try:
        Thread(None, send_one, None, (message.chat.id, f'''
🖐 Merhaba {message.from_user.first_name}. 


👍Temel komutlar:

✅ Günlük Kovid 19 Tablosunu almak için /giris yazın
🛑 Günlük Kovid 19 Tablosunu almayı durdurmak için /cikis yazın


🦠Kovid 19 Türkiye grafiği:

🙂Varsayılan kullanım:
    Varsayılan kullanım için /covid yazın
    Varsayılan kullanım;
    1️⃣5️⃣ Uzunluğu 15 blok
    0️⃣8️⃣ Genişliği 8 blok olmak üzere
    😷🤒 Türkiyenin günlük vaka grafiğini gönderir
    _Günlük vaka ve hasta toplamını gönderir_
⚙️Gelişmiş Kullanım:
    Gelişmiş kullanım için /covid yazın ve gerekli bilgileri girin
    /covid <almak istediğiniz bilgi> <uzunluk> <genişlik>
    ℹ️Eğer bir bilgiyi varsayılan olarak kullanmak istiyorsanız - yazabilirsini
    ❓Örnek kullanım:
        /covid vaka 25 5
        /covid iyilesen 50 15
        /covid vaka - 10
    💁Alabileceğiniz bilgiler:
        vaka _Bu günlük vaka ve günlük hastanın toplam sayısını verir_
        vefat _Bu günlük vefat sayısını verir_
        iyilesen _Bu günlük iyileşen sayısını verir_
        test _Bu günlük test sayısını verir_
        

⌨Satır içi komutlar:

ℹSatır içi komutlar nelerdir?
    🔴Özel sohbetler veya gruplarda Satır içi komutlar kullanarak bot ile iletişime geçebilirsiniz
    🟠Sadece @kovidbot adlı botumuzu etiketleyin ve yanına aşağıdaki komutlardan birini yazın

🦠Kovid 19 Tablosu:
    En son kovid 19 tablosunu almak için @kovidbot tablo yazabilirsiniz 
    Bu komut yazı yazma kutucuğunuzun mevcut olan en yeni kovid 19 tablosunun tarihini gösterecektir
    Bu tarihe tıklayarak o tarihteki kovid 19 tablosunu isteğiniz birine gönderebilirsiniz

📰En güncel haberler:
    Kovid 19 Hakkında en güncel haberleri almak için @kovidbot haber yazabilirsiniz
    Bunun çalışması birkaç saniye sürebilir
    Bu komut yazı yazma kutucuğunuzun üstünde birkaç resim gösterecektir
    Bunlardan birine tıklayarak o haberi istediğiniz birine gönderebilirsiniz


        ''', 'Markdown',)).start()
    except Exception as e:
        bot.send_message(
            message.chat.id, 'Bir sorunla karşılaşıldı\n' + str(e))


# Command to get curve


@ bot.message_handler(commands=["covid"])
def covid(message):
    try:
        bot.send_message(message.chat.id, 'Grafiğiniz hazırlanılıyor')
        h = 15  # height
        w = 8  # width
        get = 'gunluk_vaka'  # Thing to get
        gets = [
            'gunluk_vaka',
            'gunluk_test',
            'gunluk_iyilesen',
            'gunluk_vefat'
        ]  # All available things to get
        # The user will put one of these if he/she wants the default value
        none = ['-']
        # If the user specified the thing to get
        if len(message.text.split()) > 1:
            if message.text.split()[1] in none:
                pass
            else:
                if message.text.split()[1]:
                    # Check if it is available
                    try:
                        if 'gunluk_' + message.text.split()[1] in gets:
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
                try:
                    if message.text.split()[2] in none:
                        pass
                    else:
                        h = int(message.text.split()[2])
                except:
                    bot.send_message(
                        message.chat.id, f'{message.text.split()[2]} bir sayı değildir')
                    return
                # If the user also specified the width
                if len(message.text.split()) > 3:
                    try:
                        if message.text.split()[3] in none:
                            pass
                        else:
                            w = int(message.text.split()[3])
                    except:
                        bot.send_message(
                            message.chat.id, f'{message.text.split()[3]} bir sayı değildir')
                        return

        Thread(None, send_curve, None, (message.chat.id,
                                        {'get': get, 'h': h, 'w': w}, )).start()

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
        ids = []
        for i in temp:
            ids.append(i['_id'])
        # Check if the user is already entered
        if message.chat.id in ids:
            bot.send_message(message.chat.id, "👎🏻")
            bot.send_message(
                message.chat.id, "Zaten listede adınız bulunmakta")
        # If not
        else:
            # Insert user to our database
            Thread(target=add_db, args=(
                {'_id': message.chat.id, 'name': message.from_user.first_name},)).start()
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
        ids = []
        for i in temp:
            ids.append(i['_id'])
        # Check if the user is in our database
        if message.chat.id in ids:
            # Remove user from our database
            Thread(target=del_db, args=({'_id': message.chat.id},)).start()
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
        # Check if the user is admin (me)
        if message.chat.id == admin:
            # Get the database
            temp = getdb()
            # Prettify it
            p = ''
            for i in temp:
                p += str(i) + '\n'
            # Send
            bot.reply_to(message, p)
        else:
            bot.send_message(
                message.chat.id, 'Bu komutu kullanabilmek için admin olmalısınız')
    except Exception as e:
        bot.send_message(
            message.chat.id, 'Bir sorunla karşılaşıldı\n' + str(e))

# Inline command to send the latest covid table to someone


@ bot.inline_handler(lambda query: query.query == 'tablo')
def tablo(inline_query):
    try:
        # Get the latest covid table
        temp = cache['tablo']
        # Make it an inline command
        r = types.InlineQueryResultArticle(
            '1',
            # Title
            '📅 ' + temp[2]['tarih'] + ' 📅',
            # Content
            types.InputTextMessageContent(
                temp[2]['tarih'] + ' Tarihi için kovid 19 tablosu: \n' + temp[1] + '\n\nKovid 19 hakkında günlük bilgi almak için @kovidbot'),
            thumb_url='https://raw.githubusercontent.com/EnxGitHub/kovidbot/main/image.png?token=APVMWC6KFLK4N77RVE2BKIK7YTVYU'
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
            r.append(types.InlineQueryResultArticle(
                str(j),  # Index
                i['title'].strip(),  # Title
                thumb_url=i['urlToImage'],  # Url to image
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
