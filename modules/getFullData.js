const getData = require("./getData");

function getFullData(get, callback) {
    getData((res) => {
        let rawData = [];
        var foo = new Promise((resolve, reject) => {
            res.reverse().forEach((day) => {
                if (get == "gunluk_vaka") {
                    let cases = 0;
                    if (day["gunluk_hasta"].split(".").join("")) {
                        cases = parseInt(
                            day["gunluk_hasta"].split(".").join(""),
                        );
                    }

                    if (day["gunluk_vaka"].split(".").join("")) {
                        cases += parseInt(
                            day["gunluk_vaka"].split(".").join(""),
                        );
                    }
                    rawData.push(parseInt(cases));
                } else {
                    let specData = 0;
                    if (day[get]) {
                        specData = parseInt(day[get].split(".").join(""));
                    }
                    rawData.push(specData);
                }
            });
        });
        callback(rawData);
    });
}

module.exports = getFullData;
