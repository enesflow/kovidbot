function main(data) {
    let cases = parseInt(data["gunluk_vaka"].replace(".", ""));
    if (data["gunluk_hasta"]) {
        cases += parseInt(data["gunluk_hasta"].replace(".", ""));
    }
    return {
        case: cases,
        recovered: parseInt(data["gunluk_iyilesen"].replace(".", "")),
        death: parseInt(data["gunluk_vefat"].replace(".", "")),
        test: parseInt(data["gunluk_test"].replace(".", "")),
        date: data["tarih"],
    };
}

module.exports = main;
