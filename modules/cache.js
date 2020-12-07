let cache = {
    tablo: undefined,
    grafik: {},
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

module.exports = {
    cache: cache,
    setTablo: setTablo,
    setGrafik: setGrafik,
    flushGrafik: flushGrafik,
};
