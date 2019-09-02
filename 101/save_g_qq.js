/* save data structure to file in chrome console */
(function(console){
	console.save = function(data, filename){
		if(!data) {
			console.error('Console.save: No data')
			return;
		}
		if(!filename) filename = 'console.json'
		if(typeof data === "object"){
			data = JSON.stringify(data, undefined, 4)
		}

		var blob = new Blob([data], {type: 'text/json'}),
		e = document.createEvent('MouseEvents'),
		a = document.createElement('a')
		a.download = filename
		a.href = window.URL.createObjectURL(blob)
		a.dataset.downloadurl = ['text/json', a.download, a.href].join(':')
		e.initMouseEvent('click', true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null)
		a.dispatchEvent(e)
	}
})(console)

console.save(g_qq, 'g_qq.json');
console.save(g_qq.psm, 'g_qq.psm.json');
