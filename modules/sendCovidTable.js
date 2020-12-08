const convertData = require("./convertData");
const longMessage = require("./longMessage");
const axios = require("axios");

function sendCovidTable(data, bot) {
    axios.get("https://koved.herokuapp.com/get-secret").then((people) => {
        people["data"].forEach((person) => {
            bot.sendSticker(
                person["_id"],
                "CAACAgEAAxkBAAEBqY5fzly7WaIfk3X8BIU32hpYC25MGwACJAgAAuN4BAABeDMQjC5YwUgeBA",
            );
            bot.sendMessage(
                person["_id"],
                longMessage.daily(convertData(data), false),
            );
        });
    });
}

module.exports = sendCovidTable;
