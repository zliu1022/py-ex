#!/bin/bash
currentdir=/Users/zliu/Downloads/gameweight
echo "Drawing winrate curve in ""$currentdir"

for f in $currentdir/*
do
#fn=$(basename "$f" | cut -d'.' -f1) #get just the filename no extension
fn=$(basename "$f")".kr"
echo $f, $fn
cat gtp_0 | /Users/zliu/go/leela-zero/leelaz-dual -g -w "$f" > "$fn" 2>&1
done

for f in $currentdir/*
do
fn=$(basename "$f")".kr"
python draw_kr.py "$fn"
done
