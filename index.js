const TelegramBot = require("node-telegram-bot-api");
const NewsAPI = require("newsapi");
const moment = require("moment-timezone");
const _ = require("lodash");
const checkCovid = require("./modules/checkCovid");
const mongo = require("./modules/mongo");
const helper = require("./modules/message");
const { getPeople } = require("./modules/mongo");
const longMessage = require("./modules/longMessage");
const convertData = require("./modules/convertData");
const getData = require("./modules/getData");
const getFullData = require("./modules/getFullData");

Array.prototype.unique = function () {
    var a = this.concat();
    for (var i = 0; i < a.length; ++i) {
        for (var j = i + 1; j < a.length; ++j) {
            if (a[i] === a[j]) a.splice(j--, 1);
        }
    }

    return a;
};

const TOKEN = process.env.TOKEN;
const bot = new TelegramBot(TOKEN, { polling: true });

const queryies = ["haber", "tablo"];

const newsapi = new NewsAPI(process.env.NEWS_API);

bot.onText(/\/start/, (message) => {
    bot.sendMessage(
        message.chat.id,
        `Merhaba ${message.from.first_name}! Lütfen yardım için /help yaz.`,
    );
});

bot.onText(/\/help/, (message) => {
    bot.sendMessage(message.chat.id, longMessage.help(message.from.first_name));
});

bot.onText(/\/giris/, (message) => {
    mongo.enter(
        bot,
        { _id: message.chat.id, name: message.from.first_name },
        helper.enter,
    );
});

bot.onText(/\/cikis/, (message) => {
    mongo.leave(
        bot,
        { _id: message.chat.id, name: message.from.first_name },
        helper.leave,
    );
});

bot.onText(/\/list/, (message) => {
    let allPeople = [];
    if (message.chat.id == process.env.ADMIN) {
        getPeople((people) => {
            people.forEach((person) => {
                allPeople.push(JSON.stringify(person));
            });
            bot.sendMessage(message.chat.id, allPeople.join("\n"));
        });
    } else {
        bot.sendMessage(
            message.chat.id,
            "Bu komutu kullanabilmek için admin olmalısınız",
        );
    }
});

bot.onText(/\/covid/, (message, match) => {
    let msg = "";
    const get =
        "gunluk_" +
        (message.text.split(" ")[1] == "-"
            ? "vaka"
            : message.text.split(" ")[1] || "vaka");
    const h =
        message.text.split(" ")[2] == "-"
            ? 16
            : parseInt(message.text.split(" ")[2]) || 16;
    const w =
        message.text.split(" ")[3] == "-"
            ? 8
            : parseInt(message.text.split(" ")[3]) || 8;
    let allData = [];
    getFullData(get, (data) => {
        allData = data;
        allData = _.chunk(
            allData,
            Math.ceil(allData.length / Math.min(allData.length, h)),
        );
        for (var i = 0; i < allData.length; i++) {
            allData[i] = _.sum(allData[i]) / allData[i].length;
        }
        var divideBy = _.max(allData) / w;
        for (var i = 0; i < allData.length; i++) {
            allData[i] = Math.ceil(allData[i] / divideBy);
        }

        const emojis = ["🟩", "🟨", "🟧", "🟥"];
        allData.forEach((day) => {
            msg +=
                emojis[
                    Math.min(
                        parseInt(day / (w / emojis.length)),
                        emojis.length - 1,
                    ) || 0
                ].repeat(Math.max(day, 1)) + "\n";
        });
        bot.sendMessage(message.chat.id, msg);
    });
});

bot.on("inline_query", (query) => {
    const data = query.query;
    if (!queryies.includes(data)) {
        bot.answerInlineQuery(query.id, [
            {
                id: "0",
                type: "article",
                title: `Merhaba ${query.from.first_name}. Lütfen tablo ya da haber yaz.`,
                description: "Ya da bana tıklayabilirsin?",
                thumb_url:
                    "https://raw.githubusercontent.com/EnxGitHub/kovidbot/main/profile-picture/tinykovidbot.png",
                message_text: longMessage.spread(query.from.first_name),
            },
        ]);
    } else {
        if (data == "tablo") {
            getData((temp) => {
                let isToday = "";
                const covid = convertData(temp[0]);

                if (
                    covid["date"] == moment().tz("Turkey").format("DD.MM.YYYY")
                ) {
                    isToday = "(bugün)";
                }
                bot.answerInlineQuery(query.id, [
                    {
                        id: "0",
                        type: "article",
                        title: `📅 ${covid["date"]} ${isToday} 📅`,
                        thumb_url:
                            "https://raw.githubusercontent.com/EnxGitHub/kovidbot/main/image.png",
                        message_text: longMessage.daily(covid, true),
                    },
                ]);
            });
        }
        if (data == "haber") {
            let news = [];
            newsapi.v2
                .topHeadlines({
                    q: "korona",
                    country: "tr",
                })
                .then((response) => {
                    response["articles"].forEach((oneNew) => {
                        news.push({
                            id: String(response["articles"].indexOf(oneNew)),
                            type: "article",
                            title: oneNew["title"],
                            description: oneNew["source"]["name"],
                            thumb_url: oneNew["urlToImage"],
                            message_text: `${oneNew["description"]}\n\nHaberin tamamına ulaşmak için tıklayın: ${oneNew["url"]}\n\nBu haber https://t.me/kovidbot aracılığıyla gönderildi`,
                        });
                    });
                    newsapi.v2
                        .topHeadlines({
                            q: "kovid",
                            country: "tr",
                        })
                        .then((response2) => {
                            response2["articles"].forEach((oneNew) => {
                                news.push({
                                    id: String(
                                        response2["articles"].indexOf(oneNew) +
                                            response["totalResults"],
                                    ),
                                    type: "article",
                                    title: oneNew["title"],
                                    description: oneNew["source"]["name"],
                                    thumb_url: oneNew["urlToImage"],
                                    message_text: `${oneNew["description"]}\n\nHaberin tamamına ulaşmak için tıklayın: ${oneNew["url"]}\n\nBu haber https://t.me/kovidbot aracılığıyla gönderildi`,
                                });
                            });
                            if (news.length === 0) {
                                news.push({
                                    id: "1",
                                    type: "article",
                                    title:
                                        "Şu an için kovid 19 salgını hakkında güncel haber bulunmamaktadır",
                                    description: "@kovidbot",
                                    thumb_url:
                                        "https://raw.githubusercontent.com/EnxGitHub/kovidbot/main/profile-picture/tinykovidbot.png",
                                    message_text: longMessage.spread(
                                        query.from.first_name,
                                    ),
                                });
                            }
                            bot.answerInlineQuery(query.id, news);
                        });
                });
        }
    }
});

checkCovid(2, bot);
