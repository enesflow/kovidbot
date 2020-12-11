function main(data) {
    let cases = parseInt(data["gunluk_vaka"].split(".").join(""));
    if (data["gunluk_hasta"]) {
        cases += parseInt(data["gunluk_hasta"].split(".").join(""));
    }
    return {
        case: cases,
        recovered: parseInt(data["gunluk_iyilesen"].split(".").join("")),
        death: parseInt(data["gunluk_vefat"].split(".").join("")),
        test: parseInt(data["gunluk_test"].split(".").join("")),
        date: data["tarih"],
    };
}

module.exports = main;
