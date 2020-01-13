#!/bin/bash
currentdir=./
echo "Drawing winrate curve in ""$currentdir"
#lzdir=/home/zliu1022/go
lzdir=/Users/zliu/go/leela-zero

for f in $currentdir/*.gz
do
BASENAME="${f%.*}";
EXTENSION="${f##*.}";
fn=$BASENAME".kr"
#fn=$(basename "$f" | cut -d'.' -f1) #get just the filename no extension
echo `date +%Y-%m-%d%t%H:%M:%S`;
echo $f, $fn
cat gtp_0 | $lzdir/leelaz-dual -g -w "$f" > "$fn" 2>&1
done

for f in $currentdir/*
do
BASENAME="${f%.*}";
fn=$BASENAME".kr"
python draw_kr.py "$fn"
done
