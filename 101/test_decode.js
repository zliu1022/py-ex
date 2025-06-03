// html:
// qqdata.c = 'amsTXVcRHRATQ1cRbBwRaBFDWxIdExFCVxJsbg=='
// qqdata.r = 2
// qqdata.clone_prepos = 'amtsHxNobG0='
// qqdata.ru = 2
// 465d79e91635251efe228883c2fc4d66.js
// f_decode(qqdata.clone_prepos, "???"+qqdata.ru+qqdata.ru+qqdata.ru)
// f_decode(qqdata.c, "???"+qqdata.r+qqdata.r+qqdata.r)

/* 调用
createNewGame() {
...
this.game = QipanAPI.buildTimu???(e, this.$store.qipan.qqdata, "light" === s ? "kttheme" : "bwtheme", !0, 20 * i, (t => {
	this.radio = t;
	this.onResize(!0)
}
), this.$store.qipan.userdata.xz);
...

function A(t, e, i, o, n, a, r) {
	...
	p.test123(e);
	...
}

function f(t) {
	if (1 === t.ru || 2 === t.ru)
		for (var e = s.atob("MTAx"), i = t.ru + 1, o = e + i + i, n = 0, 
			a = ["Y29udGVudA==", "b2tfYW5zd2Vycw==", "Y2hhbmdlX2Fuc3dlcnM=", "ZmFpbF9hbnN3ZXJz", "Y2xvbmVfcG9z", "Y2xvbmVfcHJlcG9z"]; n < a.length; n++) 
		// a 解码后：content,ok_answers,change_answers,fail_answers,clone_pos,clone_prepos
		{
			var r = a[n], h = s.atob(r); "string" == typeof t[h] && (t[h] = JSON.parse(s.test202(t[h], o + i)))
		}
}

function f(t, e) {
	for (var i = u(t), s = 0, o = [], n = 0; n < i.length; ++n) {
		o.push(String.fromCharCode(i.charCodeAt(n) ^ e.charCodeAt(s)));
		s = (s + 1) % e.length
	}
	return o.join("")
}
*/
var c = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
var d = /^(?:[A-Za-z\d+\/]{4})*?(?:[A-Za-z\d+\/]{2}(?:==)?|[A-Za-z\d+\/]{3}=?)?$/;
function u_base64(t) {
	t = String(t).replace(/[\t\n\f\r ]+/g, "");
	if (!d.test(t))
		throw new TypeError("The string to be decoded is not correctly encoded.");
	t += "==".slice(2 - (3 & t.length));
	for (var e, i, s, o = "", n = 0; n < t.length; ) {
		e = c.indexOf(t.charAt(n++)) << 18 | c.indexOf(t.charAt(n++)) << 12 | (i = c.indexOf(t.charAt(n++))) << 6 | (s = c.indexOf(t.charAt(n++)));
		o += 64 === i ? String.fromCharCode(e >> 16 & 255) : 64 === s ? String.fromCharCode(e >> 16 & 255, e >> 8 & 255) : String.fromCharCode(e >> 16 & 255, e >> 8 & 255, 255 & e)
	}
	return o
}
function f_decode(t, e) {
	for (var i = u_base64(t), s = 0, o = [], n = 0; n < i.length; ++n) {
		o.push(String.fromCharCode(i.charCodeAt(n) ^ e.charCodeAt(s)));
		s = (s + 1) % e.length
	}
	return o.join("")
}

