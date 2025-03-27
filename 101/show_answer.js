function convertCoordinate(coord) {
    // 检查 coord.p 是否存在且长度为 2
    if (!coord || !coord.p || typeof coord.p !== 'string' || coord.p.length !== 2) {
        return 'Invalid coord: ' + JSON.stringify(coord);
    }
    const p = coord.p;
    // 从字符串中提取 x 和 y
    let xVal = p.charAt(0);
    let yVal = p.charAt(1);
    
    // 定义围棋棋盘的列字母表示（跳过 'I'）
    const letters = 'ABCDEFGHJKLMNOPQRST'; // 长度为19，索引0-18
    
    // 将 xVal 和 yVal 从字母转换为索引（0-18）
    function letterToIndex(letter) {
        let idx = letter.charCodeAt(0) - 'a'.charCodeAt(0);
        // 检查 idx 是否有效
        if (idx < 0 || idx > 18) {
            return -1;
        }
        return idx;
    }
    
    let xIndex = letterToIndex(xVal);
    let yIndex = letterToIndex(yVal);
    
    // 验证索引是否有效
    if (xIndex < 0 || xIndex > 18 || yIndex < 0 || yIndex > 18) {
        return 'Invalid indices: xIndex=' + xIndex + ', yIndex=' + yIndex;
    }
    
    // 将 xIndex 映射到 letters 数组，直接使用索引
    function indexToLetter(idx) {
        if (idx < 0 || idx > 18) {
            return 'Invalid index: ' + idx;
        }
        return letters.charAt(idx);
    }
    
    let column = indexToLetter(xIndex);
    // 将 yIndex 转换为棋盘上的行号（19 到 1）
    let row = 19 - yIndex;
    
    return column + row;
}

// 测试代码
const coord = { p: 'nc', c: '' };
const move = convertCoordinate(coord);
console.log('转换后的坐标:', move); // 输出: 'O17'

const outputContainer = document.createElement('div');
outputContainer.id = 'output-container';
outputContainer.style.width = '100%';
outputContainer.style.fontSize = '18px';
outputContainer.style.marginBottom = '10px';
let answerCounter = 1;
for (let i = 0; i < g_qq.answers.length; i++) {
    const ans = g_qq.answers[i];

    if (ans.ty == 1 && ans.st == 2) {
        // 创建一个段落来显示当前答案的所有坐标
        const ansParagraph = document.createElement('p');

        // 添加序号
        const indexSpan = document.createElement('span');
        indexSpan.innerText = `序号 ${answerCounter}：`; // 您可以根据需要调整序号格式
        indexSpan.style.fontWeight = 'bold';
        ansParagraph.appendChild(indexSpan);

        // 遍历 ans.pts 中的所有点
        for (let j = 0; j < ans.pts.length; j++) {
            const coord = ans.pts[j];
            const move = convertCoordinate(coord);

            // 创建一个 span 来容纳每个坐标
            const moveSpan = document.createElement('span');
            moveSpan.innerText = move + ' ';

            if (j % 2 === 0) {
                // 当 j 为偶数时，应用特殊样式
                moveSpan.style.fontWeight = 'bold'; // 字体加粗
                moveSpan.style.backgroundColor = 'black'; // 背景色为黑色
                moveSpan.style.color = 'white'; // 字体颜色为白色
            }

            // 将 span 添加到段落中
            ansParagraph.appendChild(moveSpan);
        }

        // 添加到输出容器中
        outputContainer.appendChild(ansParagraph);

        // 序号加一
        answerCounter++;
    }
}
document.body.insertBefore(outputContainer, document.body.firstChild);
