var outsgf = function() {
    var f1 = document.getElementById("frame1");
    var new_qq = null;
    var new_location = null;
    var new_document = null;
    if (f1 != null) {
        console.log('从frame中获取信息');
        new_qq = f1.contentWindow.g_qq;
        new_location = f1.src;
        new_document = f1.contentDocument;
    } else {
        new_qq = g_qq;
        new_location = location.href;
        new_document = document;
    }

    var str;
    str = "(;GM[1]FF[4]CA[UTF-8]KM[7.5]SZ[" + new_qq.psm.lu + "]PB[]PW[]";
    str += "CP[" + new_location + "]";

    str += "\nAB";
    for (i = 0; i < new_qq.psm.prepos[0].length; i++)
        str += "[" + new_qq.psm.prepos[0][i] + "]";
    str += "\nAW";
    for (i = 0; i < new_qq.psm.prepos[1].length; i++)
        str += "[" + new_qq.psm.prepos[1][i] + "]";

    /*if (new_qq.psm.is_start_black != true) {
        str += "\n;B[]"
    }*/

    str += '\nC[';
    var tmpbread = new_document.getElementsByClassName("breadcrumb")[0];
    var n = new_location.split("/");
    var filename = n[3] + '-' + n[4] + '-' + n[n.length - 2] + ".sgf";
    if (tmpbread && tmpbread.children.length > 3) {
        console.log(tmpbread.children[0].textContent, tmpbread.children[1].textContent, tmpbread.children[2].textContent);
        str += tmpbread.children[0].textContent + '\n' + tmpbread.children[1].textContent  + '\n' +tmpbread.children[2].textContent;
    }
    console.log(new_qq.qtypename, new_qq.title, new_qq.levelname);
    str += new_qq.qtypename+ '\n' + new_qq.title+ '\n' +new_qq.levelname;
    str += ']';

    console.log('共', new_qq.answers.length, '条答案');
    //console.log("nu step isdest st ty v ok bad change error name");
    for (i = 0; i < new_qq.answers.length; i++) {
        var an = new_qq.answers[i];
        var type = (an.ty == 1) ? '正解' : (an.ty == 3) ? '失败' : (an.ty == 2) ? '变化' : (an.ty == 4) ? '淘汰' : '未知';
        var status = (an.st == 2) ? '审完' : (an.st == 1) ? '待审' : '未知';

        //var pv = '\n(C[第'+an.nu+'答案]';
        var pv = '\n(';
        var prn_pv = (new_qq.blackfirst == true) ? 'B ' : 'W ';
        for (j = 0; j < new_qq.answers[i].pts.length; j++) {
            var x = "ABCDEFGHJKLMNOPQRST"['abcdefghijklmnopqrst'.indexOf(new_qq.answers[i].pts[j].p[0])];
            var y = 19 - 'abcdefghijklmnopqrst'.indexOf(new_qq.answers[i].pts[j].p[1]);
            prn_pv += x + y + ' ';
            if (new_qq.blackfirst == true) {
                pv += ";" + ((j % 2 == 0) ? "B" : "W") + "[" + new_qq.answers[i].pts[j].p + "]";
            } else {
                pv += ";" + ((j % 2 == 0) ? "W" : "B") + "[" + new_qq.answers[i].pts[j].p + "]";
            }
        }
        pv += ')';

        console.log('no.', an.nu, an.stepcount, an.isdest, status, type, an.v, prn_pv, ':', an.ok_count, an.bad_count, an.change_count, an.error_count, an.username);
        //if(new_qq.answers[i].isdest==true){
        //if (new_qq.answers[i].nu == 1) {
        if (new_qq.answers[i].ty == 1 && new_qq.answers[i].st==2) {
            str += pv;
        }
    }

    str += "\n)"
    return str;
}

var savesgf = function() {
    var f1 = document.getElementById("frame1");
    var new_qq = null;
    var new_location = null;
    var new_document = null;
    if (f1 != null) {
        new_qq = f1.contentWindow.g_qq;
        new_location = f1.src;
        new_document = f1.contentDocument;
    } else {
        new_qq = g_qq;
        new_location = location.href;
        new_document = document;
    }

    var tmpbread = new_document.getElementsByClassName("breadcrumb")[0];
    var n = new_location.split("/");
    var filename = n[3] + '-' + n[4] + '-' + n[n.length - 2] + ".sgf";
    /*
    if (tmpbread && tmpbread.children.length > 3) {
        console.log(tmpbread.children[0].textContent, tmpbread.children[1].textContent, tmpbread.children[2].textContent);
    }
    console.log(new_qq.qtypename, new_qq.title, new_qq.levelname);*/

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

var timeout = 1;
var count = 0;
var maxcount = 3;
var current = location.href;
nextpage();

function nextpage() {
    count++;
    console.log('下载第 ' + count + ' 题');

    //outsgf();
    savesgf();

    if (count >= maxcount) {
        console.log('count超出范围，停止');
        return;
    }

    var f1 = document.getElementById("frame1");
    var pageid = "nextq"
    var t1 = document.getElementById(pageid);
    var t2 = null;
    if (t1 == null) {
        var tmpbtn = document.getElementsByClassName("btn btn-info");
        if (tmpbtn.length != 0 && tmpbtn[0].text == ' 下 一 题 ') {
            t1 = tmpbtn[0];
        } else if (tmpbtn.length != 0 && tmpbtn[1].text == ' 下 一 题 ') {
            t1 = tmpbtn[1];
        }
    }

    if (f1 != null) {
        t2 = f1.contentDocument.getElementById(pageid);
        if (t2 == null) {
            var tmpbtn = f1.contentDocument.getElementsByClassName("btn btn-info");
            if (tmpbtn[0].text == ' 下 一 题 ') {
                t2 = tmpbtn[0];
            } else if (tmpbtn.length > 1 && tmpbtn[1].text == ' 下 一 题 ') {
                t2 = tmpbtn[1];
            }
        }
    }

    if (t1 != null) {
        current = t1.href;
        console.log('从document直接获取，启动', timeout, '秒定时器，跳转到下一题', current);
        setTimeout('nextpage()', 1000 * timeout);
    } else if (t2 != null) {
        current = t2.href;
        console.log('从frame间接获取，启动', timeout, '秒定时器，跳转到下一题', current);
        setTimeout('nextpage()', 1000 * timeout);
    } else {
        console.log('没有下一页了，停止');
        return;
    }

    fr4me = '<frameset id="frameset1" cols=\'*\'>\n<frame id="frame1" src=\'' + current + '\'/>';
    fr4me += '</frameset>';
    with (document) {
        write(fr4me);
        void (close())
    }
    ;
}

// if it's previous page, should be below:
//var t=document.getElementsByClassName("previous");
//location.replace(t[0].children[0].href);

