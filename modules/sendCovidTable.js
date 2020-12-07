const convertData = require("./convertData");
const longMessage = require("./longMessage");

function sendCovidTable(data, bot) {
    console.log(longMessage.daily(convertData(data), false));
}

module.exports = sendCovidTable;
