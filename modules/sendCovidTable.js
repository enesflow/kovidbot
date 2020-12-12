const convertData = require("./convertData");
const mongo = require("./mongo");
const longMessage = require("./longMessage");
const axios = require("axios");
const _ = require("lodash");

function sendCovidTable(data, bot) {
    mongo.getAds((ads) => {
        axios.get("http://localhost:8001/get-secret").then((people) => {
            people["data"].forEach((person) => {
                const chatId = person["_id"];
                Promise.resolve(
                    bot.sendMessage(
                        chatId,
                        longMessage.daily(convertData(data), false),
                    ),
                ).then(() => {
                    if (!person["pro"]) {
                        const ad = _.sample(ads);
                        Promise.resolve(
                            bot.sendPhoto(chatId, ad["image"], {
                                caption: ad["title"],
                            }),
                        ).then(() => {
                            bot.sendMessage(chatId, ad["message"].join("\n"));
                        });
                    }
                });
            });
        });
    });
}

module.exports = sendCovidTable;
