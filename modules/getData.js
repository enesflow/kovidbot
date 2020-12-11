const fetch = require("node-fetch");
const JSSoup = require("jssoup").default;
const URL =
    "https://covid19.saglik.gov.tr/TR-66935/genel-koronavirus-tablosu.html";

function getData(callback) {
    const response = Promise.resolve(fetch(URL));
    response.then((res) => {
        const text = res.text();
        text.then((res) => {
            const soup = new JSSoup(res);
            const scripts = soup.findAll("script");
            const json = Promise.resolve(
                JSON.parse(
                    scripts[scripts.length - 1].text
                        .slice(36)
                        .split(";//]]>")
                        .join(""),
                ),
            ).then((j) => {
                callback(j);
            });
        });
    });
}

module.exports = getData;
