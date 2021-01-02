const moment = require("moment-timezone");
const mongo = require("./mongo");
const sendCovidTable = require("./sendCovidTable");
const cache = require("./cache");
const getData = require("./getData");

function checkCovid(time, bot) {
    const interval = setInterval(() => {
        console.log("Checking");
        cache.setNews([]);
        getData((json) => {
            const date = json[0]["tarih"];
            const today = moment().tz("Turkey").format("DD.MM.YYYY");
            mongo.getChecked((checked) => {
                cache.setTablo(json[0]);
                if (date == today && !checked) {
                    mongo.setChecked(true, () => {});
                    console.log("Now");
                    sendCovidTable(json[0], bot);
                    cache.flushGrafik();
                    cache.flushFull();
                } else {
                    console.log("Not Now");
                    console.log("Date:", date, today);
                }
                if (date != today && checked) {
                    mongo.setChecked(false, () => {});
                }
            });
            console.log("Checked");
            getDelay((delay) => {
                time = delay;
                console.log("Delay is", time);
                clearInterval(interval);
                checkCovid(time, bot);
            });
        });
    }, 1000 * time);
}

function getDelay(callback) {
    mongo.getChecked((checked) => {
        console.log("Checked is", checked);
        const time = [
            [100, 60 * 5],
            [18, 80],
            [19, 40],
            [20, 20],
            [21, 10],
        ];

        const hour = parseInt(moment().tz("Turkey").format("HH"));
        let delay = time[0][1];
        for (var i = 0; i < time.length; i++) {
            if (hour >= time[i][0]) {
                delay = time[i][1];
            }
        }
        if (checked) {
            delay = time[0][1];
        }
        callback(delay);
    });
}

module.exports = checkCovid;
