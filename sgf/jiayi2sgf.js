(function(console) {
    console.save = function(data, filename) {
        const blob = new Blob([data],{
            type: "application/x-go-sgf"
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }
    ;
}
)(console);

function convertToSGF(arr) {
    let sgf = "(;FF[4]GM[1]SZ[19]";
    const letterMapping = "abcdefghijklmnopqrs";
    for (let i = 0; i < arr.length; i++) {
        const step = arr[i];
        const x = (step[0] - 1) % 19;
        const y = Math.floor((step[0] - 1) / 19);
        const color = step[1] % 2 === 1 ? "B" : "W";
        const sgfMove = ";" + color + "[" + letterMapping[x] + letterMapping[y] + "]";
        sgf += sgfMove;
    }
    sgf += ")";
    return sgf;
}

function getFileName(info) {
    let data_str = info['play_time'].split(' ')[0];
    let result_str = '';
    if (info['player'] == 1) {
        if (info['u_id_1'] == "451213")
            result_str = '，执黑'
        else
            result_str = '，执白'
    } else {
        if (info['u_id_1'] == "451213")
            result_str = '，执白'
        else
            result_str = '，执黑'
    }

    if (info['winner'] == "451213")
        win_str = '胜'
    else
        win_str = '败'
    if (Math.abs(info['win_over']) == 0){
        result_str +=  '，中盘' + win_str
    }else{
        result_str +=  '，' + win_str + Math.abs(info['win_over']) + '子'    
    }
    
    return data_str + result_str + '.sgf'
}

const sgf = convertToSGF(chessData(arr));
console.save(sgf, getFileName(info));

