/* Snippets in chrome: save 101 data to sgf file */
var outsgf = function() {
    var str;
    str = "(;GM[1]FF[4]CA[UTF-8]KM[7.5]SZ[" + g_qq.lu + "]PB[]PW[]";
    str += "CP[" + location.href + "]";
    str += "\nAB";
    for (i = 0; i < g_qq.prepos[0].length; i++)
        str += "[" + g_qq.prepos[0][i] + "]";
    str += "\nAW";
    for (i = 0; i < g_qq.prepos[1].length; i++)
        str += "[" + g_qq.prepos[1][i] + "]";
    /*
        var n = 0;
        for(var i in g_qq.andata){
            if (g_qq.andata[i].pt.length!=0){
                str += "\n;"+((n%2==0)?"W":"B")+"["+g_qq.andata[i].pt+"]";
            }
            n++;
        };
        */
    if (g_qq.blackfirst != true) {
        str += "\n;B[]"
    }
    console.log("i name step ok bad change error isdest nu st ty v");
    for (i = 0; i < g_qq.answers.length; i++) {
        console.log(i, g_qq.answers[i].username, g_qq.answers[i].stepcount, g_qq.answers[i].ok_count, g_qq.answers[i].bad_count, g_qq.answers[i].change_count, g_qq.answers[i].error_count, g_qq.answers[i].isdest, g_qq.answers[i].nu, g_qq.answers[i].st, g_qq.answers[i].ty, g_qq.answers[i].v);
        //if(g_qq.answers[i].isdest==true){
        if (g_qq.answers[i].nu == 1) {
            for (j = 0; j < g_qq.answers[i].pts.length; j++) {
                if (g_qq.blackfirst == true) {
                    str += "\n;" + ((j % 2 == 0) ? "B" : "W") + "[" + g_qq.answers[i].pts[j].p + "]";
                } else {
                    str += "\n;" + ((j % 2 == 0) ? "W" : "B") + "[" + g_qq.answers[i].pts[j].p + "]";
                }

            }
        }
    }
    str += "\n)"
    //console.log(str);
    return str;
}
var savesgf = function() {
    var n = location.href.split("/");
    var filename = n[n.length - 2] + ".sgf";
    var data = outsgf();
    if (!data) {
        console.error('Console.save: No data')
        return;
    }
    if (!filename)
        filename = 'console.json'
    if (typeof data === "object") {
        data = JSON.stringify(data, undefined, 4)
    }

    var blob = new Blob([data],{
        type: 'text/json'
    })
      , e = document.createEvent('MouseEvents')
      , a = document.createElement('a')
    a.download = filename
    a.href = window.URL.createObjectURL(blob)
    a.dataset.downloadurl = ['text/json', a.download, a.href].join(':')
    e.initMouseEvent('click', true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null)
    a.dispatchEvent(e)
}

var listsgf = function() {
    var q = document.getElementsByClassName("questionitem");
    for (i = 0; i < q.length; i++) {
        var t = q[i].children[0].children[0].href;
        console.log(t);
        //location.replace(t.children[0].children[0].href);
        //window.location.href=t.children[0].children[0].href;
    }
}

savesgf();
var t = document.getElementById("nextq");
location.replace(t.href);

// if it's previous page, should be below:
//var t=document.getElementsByClassName("previous");
//location.replace(t[0].children[0].href);

