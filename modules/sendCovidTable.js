const convertData = require("./convertData");
const longMessage = require("./longMessage");
const axios = require("axios");
const _ = require("lodash");
require("dotenv").config();

async function sendCovidTable(data, bot) {
    const ads = await axios.get(
        "http://kovidbot.herokuapp.com/" +
            process.env.GETADS +
            process.env.SECRET,
    );
    const sendAds = [];
    const people = await axios.get(
        "http://kovidbot.herokuapp.com/" + process.env.GET + process.env.SECRET,
    );
    await people["data"].forEach(async (person) => {
        const chatId = person["_id"];
        console.log(person["name"]);
        bot.sendMessage(chatId, longMessage.daily(convertData(data), false));
        if (!person["pro"]) {
            sendAds.push(person);
        }
    });
    sendAds.forEach(async (person) => {
        const ad = _.sample(ads["data"]);
        if (ad) {
            bot.sendPhoto(person["_id"], ad["imgurl"], {
                caption: ad["message"].join("\n"),
            });
        }
    });
}

module.exports = sendCovidTable;
