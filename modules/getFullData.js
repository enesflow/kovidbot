const getData = require("./getData");
const _ = require("lodash");

function getFullData(get, callback) {
    getData((res) => {
        let rawData = [];
        var foo = new Promise((resolve, reject) => {
            res.reverse().forEach((day) => {
                if (get == "gunluk_vaka") {
                    let cases = 0;
                    if (day["gunluk_hasta"].replace(".", "")) {
                        cases = parseInt(day["gunluk_hasta"].replace(".", ""));
                    }

                    if (day["gunluk_vaka"].replace(".", "")) {
                        cases += parseInt(day["gunluk_vaka"].replace(".", ""));
                    }
                    rawData.push(parseInt(cases));
                } else {
                    let specData = 0;
                    if (day[get]) {
                        specData = parseInt(day[get].replace(".", ""));
                    }
                    rawData.push(specData);
                }
            });
        });
        callback(rawData);
    });
}

module.exports = getFullData;
