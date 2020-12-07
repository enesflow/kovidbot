const convertData = require("./convertData");
const longMessage = require("./longMessage");
const mongo = require("./mongo");

function sendCovidTable(data, bot) {
    mongo.getPeople.forEach((person) => {
        bot.sendMessage(person, longMessage.daily(convertData(data), false));
    });
}

module.exports = sendCovidTable;
