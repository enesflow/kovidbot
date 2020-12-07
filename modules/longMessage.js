const beautify = require("./beautify");

function help(name) {
    return `🖐 Merhaba ${name}. 
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
            `;
}

function spread(name) {
    return `👋Merhaba Ben @kovidbot!
🌐${name} Arkadaşımızın yardımıyla uçsuz bucaksız internette size ulaşabildim

🤖Ben bir Telegram botuyum. 


❓Ne yapabilirim?

⚡Türkiye kovid 19 tablosu açıklandığında saniyeler içerisinde bu tabloyu sana ulaştırabilirim,
📰En güncel kovid 19 haberlerini sana gösterebilirim,
📱Benim sayemde arkadaşlarınıza en güncel kovid 19 tablosunu ve en güncel haberleri gönderebilirsiniz,
💪Saniyeler içerisinde size istediğiniz şekilde kovid 19 grafiğini gösterebilirim

🧐O zaman ne duruyorsunuz? Hemen tıklayın 👉 t.me/kovidbot`;
}

function daily(data, isSpread) {
    let res = "";
    res += `📅 Tarih ${data["date"]}

🧪 Test sayısı: ${beautify(data["test"])}
🤒 Vaka sayısı: ${beautify(data["case"])}
💀 Vefat sayısı: ${beautify(data["death"])}
☺️ İyileşen sayısı: ${beautify(data["recovered"])}`;
    if (isSpread) {
        return (
            res +
            "\n\n\nKovid 19 tablosu açıklandığında anında haber almak için tıklayın \n👉 https://t.me/kovidbot"
        );
    } else {
        return res;
    }
}

module.exports = {
    help: help,
    spread: spread,
    daily: daily,
};
