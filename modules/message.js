async function enter(bot, data, success) {
    if (success) {
        await bot.sendSticker(
            data["_id"],
            "CAACAgIAAxkBAAEBp8pfy6gnywhe-XfV_BwOuTBU7GaSkAAC_gADVp29CtoEYTAu-df_HgQ",
        );
        bot.sendMessage(data["_id"], "Başarıyla giriş yapıldı!");
    } else {
        await bot.sendSticker(
            data["_id"],
            "CAACAgIAAxkBAAEBp9Bfy6j2ihT4hb4gtRsHIZwAASh8B4kAAvkAA1advQqVZW6rKisbNh4E",
        );
        bot.sendMessage(data["_id"], "Zaten listede adınız bulunmakta!");
    }
}

async function leave(bot, data, success) {
    if (success) {
        await bot.sendSticker(
            data["_id"],
            "CAACAgIAAxkBAAEBp9Jfy6pNSPtYpfk26MWByaUMDlZKCwAC8wADVp29Cmob68TH-pb-HgQ",
        );
        bot.sendMessage(
            data["_id"],
            "Çıkış yaptığınıza çok üzgünüz. \nTekrar giriş yapmak için /giris yazabilirsiniz",
        );
    } else {
        await bot.sendSticker(
            data["_id"],
            "CAACAgIAAxkBAAEBp9Rfy6qQcOLlutmiMaiQK3R0lTvpHwACAQEAAladvQoivp8OuMLmNB4E",
        );
        bot.sendMessage(
            data["_id"],
            "Zaten listede adınız bulunmamakta. \nAma giriş yapmak için /giris yazabilirsiniz",
        );
    }
}

module.exports = {
    enter: enter,
    leave: leave,
};
