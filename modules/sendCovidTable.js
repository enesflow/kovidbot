const convertData = require("./convertData");
const longMessage = require("./longMessage");
const mongo = require("./mongo");

function sendCovidTable(data, bot) {
    mongo.getPeople((people) => {
        people.forEach((person) => {
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
