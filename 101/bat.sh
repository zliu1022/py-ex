#!/bin/bash
currentdir=/Users/zliu/go/sgf/4K/
#currentdir=/Users/zliu/Downloads/

for f in $currentdir*.sgf
do
#echo $f
cat "$f" | grep '中盘作战题' > /dev/null
#实战题
#官子题
#布局题
#手筋题
#棋理题
#模仿题
#欣赏题
#死活题
#落子题
#中盘作战题
#布局猜子题
if [ $? -eq 0 ]; then
echo $f
fi
done

