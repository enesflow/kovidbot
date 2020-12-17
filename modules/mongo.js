const { MongoClient } = require("mongodb");
require("dotenv").config();

const uri = process.env.MONGO;
const client = new MongoClient(uri, { useUnifiedTopology: true });
client.connect();
async function isIn(who) {
    const db = await client.db("kovid").collection("people");
    Promise.resolve(db.find(who))
        .then((res) => {
            res.toArray((err, result) => {
                if (result != []) {
                    return true;
                } else {
                    return false;
                }
            });
        })
        .catch((err) => console.log("ERROR: ", err));
}

async function getPeople(callback) {
    const db = await client.db("kovid").collection("people");
    Promise.resolve(db.find({}))
        .then((res) => {
            res.toArray((err, result) => {
                callback(result);
            });
        })
        .catch((err) => console.log("ERROR: ", err));
}

async function enter(bot, data, callback) {
    const db = await client.db("kovid").collection("people");
    Promise.resolve(db.find(data))
        .then((res) => {
            res.toArray((err, result) => {
                if (result.length == 0) {
                    db.insertOne(data, (err, res) => {
                        if (err) {
                            callback(bot, data, false);
                            console.log("ERROR: ", err);
                        } else {
                            callback(bot, data, true);
                        }
                    });
                } else {
                    callback(bot, data, false);
                }
            });
        })
        .catch((err) => console.log("ERROR: ", err));
}

async function leave(bot, data, callback) {
    const db = await client.db("kovid").collection("people");
    Promise.resolve(db.find(data))
        .then((res) => {
            res.toArray((err, result) => {
                if (result.length != 0) {
                    db.deleteOne(data, (err, res) => {
                        if (err) {
                            callback(bot, data, false);
                            console.log("ERROR: ", err);
                        } else {
                            callback(bot, data, true);
                        }
                    });
                } else {
                    callback(bot, data, false);
                }
            });
        })
        .catch((err) => console.log("ERROR: ", err));
}

async function setChecked(to, callback) {
    const db = await client.db("kovid").collection("info");
    Promise.resolve(db.updateOne({ _id: 0 }, { $set: { checked: to } }))
        .then((err, res) => {
            if (err) console.dir(err);
            callback(res);
        })
        .catch((err) => console.log("ERROR: ", err));
}

async function getChecked(callback) {
    const db = await client.db("kovid").collection("info");
    Promise.resolve(db.findOne({ _id: 0 }))
        .then((res) => {
            callback(res["checked"]);
        })
        .catch((err) => console.log("ERROR: ", err));
}

async function getAds(callback) {
    const db = await client.db("kovid").collection("ads");
    db.find({}).toArray((err, arr) => {
        if (err) console.dir(err);
        callback(arr);
    });
}

async function addAd(bot, data, callback) {
    const db = await client.db("kovid").collection("ads");
    Promise.resolve(db.find(data))
        .then((res) => {
            res.toArray((err, result) => {
                if (result.length == 0) {
                    db.insertOne(data, (err, res) => {
                        if (err) {
                            callback(bot, data, false, err);
                            console.log("ERROR: ", err);
                        } else {
                            callback(bot, data, true, undefined);
                        }
                    });
                } else {
                    callback(
                        bot,
                        data,
                        false,
                        "The ad is already in the database",
                    );
                }
            });
        })
        .catch((err) => {
            console.log("ERROR: ", err);
            callback(bot, data, false, err);
        });
}
async function removeAd(bot, data, callback) {
    const db = await client.db("kovid").collection("ads");
    Promise.resolve(db.find(data))
        .then((res) => {
            console.log(res);
            res.toArray((err, result) => {
                if (result.length != 0) {
                    db.deleteOne(data, (err, res) => {
                        if (err) {
                            callback(bot, data, false, err);
                            console.log("ERROR: ", err);
                        } else {
                            callback(bot, data, true, undefined);
                        }
                    });
                } else {
                    callback(
                        bot,
                        data,
                        false,
                        "There are no ads that match these requirements ",
                    );
                }
            });
        })
        .catch((err) => {
            console.log("ERROR: ", err);
            callback(bot, data, false, err);
        });
}

module.exports = {
    getPeople: getPeople,
    enter: enter,
    leave: leave,
    setChecked: setChecked,
    getChecked: getChecked,
    getAds: getAds,
    addAd: addAd,
    removeAd: removeAd,
};
