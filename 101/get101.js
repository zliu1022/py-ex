"use strict";

var filename = '';
var typename = ['未知0', '死活题', '手筋题', '未知3', '布局题', '官子题', '未知6', '未知7', '欣赏题', '未知9', '中盘作战题', '模仿题', '棋理题'];

var outsgf = function() {
    var f1 = document.getElementById("frame1");
    var new_qq = null;
    var new_location = null;
    var new_document = null;
    if (f1 != null) {
        //console.log('从frame中获取信息');
        new_qq = f1.contentWindow.g_qq;
        new_location = f1.contentWindow.location.href;
        new_document = f1.contentDocument;
    } else {
        new_qq = g_qq;
        new_location = location.href;
        new_document = document;
    }
    var n = new_location.split("/");
    //filename = n[3] + '-' + n[4] + '-' + n[n.length - 2] + ".sgf";
    var n1 = new_document.title.split(" ")[0];
    filename = new_qq.levelname + '-' + n1 + ".sgf";

    var str;
    str = "(;GM[1]FF[4]CA[UTF-8]KM[7.5]SZ[" + new_qq.psm.lu + "]PB[]PW[]";
    str += "CP[" + new_location + "]";

    if (new_qq.qtype == 11) {
        if (new_qq.clone_prepos.length) {
            str += "\nAB";
            for (var i = 0; i < new_qq.clone_prepos[0].length; i++) {
                var clone = new_qq.clone_prepos[0][i];
                str += '[' + clone + ']';
            }
            str += "\nAW";
            for (var i = 0; i < new_qq.clone_prepos[1].length; i++) {
                var clone = new_qq.clone_prepos[1][i];
                str += '[' + clone + ']';
            }
            str += '\n';
        }
    } else if (new_qq.psm.prepos.length) {
        str += "\nAB";
        for (var i = 0; i < new_qq.psm.prepos[0].length; i++)
            str += "[" + new_qq.psm.prepos[0][i] + "]";
        str += "\nAW";
        for (var i = 0; i < new_qq.psm.prepos[1].length; i++)
            str += "[" + new_qq.psm.prepos[1][i] + "]";
        /*
        if (new_qq.psm.is_start_black != true) {
        str += "\n;B[]"
        }
        */
    }

    str += '\nC[\n';
    str += 'title:' + new_document.title + '\n';
    console.log(filename, new_document.title, new_qq.qtypename, new_qq.title, new_qq.levelname, new_qq.name, new_location);
    console.log(typename[new_qq.qtype], '共', new_qq.options.length, '个选项', new_qq.answers.length, '条答案', new_qq.attr_type, new_qq.clone_pos, new_qq.clone_prepos, new_qq.taotaiid, new_qq.doingtype, new_qq.xuandians);
    //console.log(new_qq.hasbook, new_qq.bookinfos);
    //console.log(new_qq.psm.qtype, new_qq.psm.doingtype);

    var tmpbread = new_document.getElementsByClassName("breadcrumb")[0];
    //var n = new_location.split("/");
    //var filename = n[3] + '-' + n[4] + '-' + n[n.length - 2] + ".sgf";
    if (tmpbread) {
        for (var i = 0; i < (tmpbread.children.length - 1); i++) {
            //console.log('subtitle'+i+':', tmpbread.children[i].textContent);
            str += tmpbread.children[i].textContent + '\n';
        }
    }
    str += '\n';
    str += 'qtypename:' + new_qq.qtypename + '\n' + 'title:' + new_qq.title + '\n' + 'levelname:' + new_qq.levelname + '\n' + 'name:' + new_qq.name + '\n';

    //console.log('共', new_qq.options.length, '个选项', new_qq.answers.length, '条答案');
    //new_qq.psm.options.length
    str += '\n选项：\n';
    for (var i = 0; i < new_qq.options.length; i++) {
        var opt = new_qq.options[i];
        //var opt1 = new_qq.psm.options[i];
        str += opt.indexname + ' ' + opt.content + opt.isok + '\n';
    }
    str += ']';

    if (new_qq.qtype == 11) {
        str += '\n';
        for (var i = 0; i < new_qq.clone_pos.length; i++) {
            var clone = new_qq.clone_pos[i];
            //str += '[' + clone +':'+ (i+1) + ']' ;
            if (new_qq.blackfirst == true) {
                str += ";" + ((i % 2 == 0) ? "B" : "W") + "[" + clone + "]";
            } else {
                str += ";" + ((i % 2 == 0) ? "W" : "B") + "[" + clone + "]";
            }
        }
        str += '\n';
    }

    //console.log("nu step isdest st ty v ok bad change error name");
    for (var i = 0; i < new_qq.answers.length; i++) {
        var an = new_qq.answers[i];
        var type = (an.ty == 1) ? '正解' : (an.ty == 3) ? '失败' : (an.ty == 2) ? '变化' : (an.ty == 4) ? '淘汰' : '未知';
        var status = (an.st == 2) ? '审完' : (an.st == 1) ? '待审' : '未知';

        //var pv = '\n(C[第'+an.nu+'答案]';
        var pv = '\n(';
        var prn_pv = (new_qq.blackfirst == true) ? 'B ' : 'W ';
        for (var j = 0; j < new_qq.answers[i].pts.length; j++) {
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

        //console.log('no.', an.nu, an.stepcount, an.isdest, status, type, an.v, prn_pv, ':', an.ok_count, an.bad_count, an.change_count, an.error_count, an.username);
        //if(new_qq.answers[i].isdest==true){
        //if (new_qq.answers[i].nu == 1) {
        if (new_qq.answers[i].ty == 1 && new_qq.answers[i].st == 2) {
            str += pv;
        }
    }

    str += "\n)"
    return str;
}

var savesgf = function() {
    var data = outsgf();
    if (!data) {
        console.error('Console.save: No data')
        return;
    }
    //console.log('filename:', filename);
    if (!filename)
        filename = 'console.json'
    if (typeof data === "object") {
        data = JSON.stringify(data, undefined, 4)
    }

    var e = document.createEvent('MouseEvents');
    var a = document.createElement('a');
    var blob = new Blob([data],{
        type: 'text/json'
    })

    /*
    var blob = new Blob([data],{
        type: 'text/json'
    })
      , e = document.createEvent('MouseEvents')
      , a = document.createElement('a')
      */
    a.download = filename
    a.href = window.URL.createObjectURL(blob)
    a.dataset.downloadurl = ['text/json', a.download, a.href].join(':')
    e.initMouseEvent('click', true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null)
    a.dispatchEvent(e)
}

var listsgf = function() {
    var q = document.getElementsByClassName("questionitem");
    for (var i = 0; i < q.length; i++) {
        var t = q[i].children[0].children[0].href;
        console.log(t);
        //location.replace(t.children[0].children[0].href);
        //window.location.href=t.children[0].children[0].href;
    }
}

var timemid = 10;
//随机等待的时间中位数 10
var timerange = 16;
//随机等待的时间范围 16
var count = 0;
var maxcount = 9999;
//var current = location.href;
nextpage();

function nextpage() {
    count++;
    console.log('\n下载第 ' + count + ' 题');

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
        if (tmpbtn.length != 0 && typeof(tmpbtn[0].text)!='undefined' && tmpbtn[0].text == ' 下 一 题 ') {
            t1 = tmpbtn[0];
        } else if (tmpbtn.length != 0 && tmpbtn[1].text == ' 下 一 题 ') {
            t1 = tmpbtn[1];
        }
    }

    if (f1 != null) {
        t2 = f1.contentDocument.getElementById(pageid);
        if (t2 == null) {
            var tmpbtn = f1.contentDocument.getElementsByClassName("btn btn-info");
            if (tmpbtn.length != 0 && typeof(tmpbtn[0].text)!='undefined' && tmpbtn[0].text == ' 下 一 题 ') {
                t2 = tmpbtn[0];
            } else if (tmpbtn.length > 1 && tmpbtn[1].text == ' 下 一 题 ') {
                t2 = tmpbtn[1];
            }
        }
    }

    var current = '';
    var timeout = Math.random() * timerange - (timerange / 2) + timemid;
    if (t1 != null) {
        current = t1.href;
        console.log('从document直接获取，启动', timeout, '秒定时器，跳转到下一题', current);
        setTimeout('nextpage()', 1000 * timeout);
    } else if (t2 != null) {
        current = t2.href;
        //console.log('从frame间接获取，启动', timeout, '秒定时器，跳转到下一题', current);
        setTimeout('nextpage()', 1000 * timeout);
    } else {
        console.log('没有下一页了，停止');
        return;
    }

    var fr4me = '<frameset id="frameset1" cols=\'*\'>\n<frame id="frame1" src=\'' + current + '\'/>' + '</frameset>';

    if (f1 != null) {
        //f1.src = "";
        f1.src = 'about:blank';
        f1 = null;
    }
    t1 = null;
    t2 = null;
    current = null;

    document.write(fr4me);
    document.close();
    /*
    with (document) {
        write(fr4me);
        void (close())
    }
    ;
    */
}

// if it's previous page, should be below:
//var t=document.getElementsByClassName("previous");
//location.replace(t[0].children[0].href);

