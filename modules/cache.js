let cache = {
    tablo: undefined,
    grafik: {},
    full: undefined,
    ads: [],
    news: [],
};

const setTablo = (to) => {
    cache["tablo"] = to;
};

const flushGrafik = () => {
    cache["grafik"] = {};
};

const setGrafik = (get, to) => {
    cache["grafik"][get] = to;
};

const setFull = (to) => {
    cache["full"] = to;
};

const flushFull = () => {
    cache["full"] = undefined;
};

const setAds = (to) => {
    cache["ads"] = to;
};

const setNews = (to) => {
    cache["news"] = to;
};

module.exports = {
    cache: cache,
    setTablo: setTablo,
    setGrafik: setGrafik,
    flushGrafik: flushGrafik,
    setFull: setFull,
    flushFull: flushFull,
    setNews: setNews,
};
