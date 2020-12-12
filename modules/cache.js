let cache = {
    tablo: undefined,
    grafik: {},
    ads: [],
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

const setAds = (to) => {
    cache["ads"] = to;
};

module.exports = {
    cache: cache,
    setTablo: setTablo,
    setGrafik: setGrafik,
    flushGrafik: flushGrafik,
};
