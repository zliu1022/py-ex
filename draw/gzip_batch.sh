#!/bin/bash
currentdir=/Users/zliu/Downloads/gameweight

for f in $currentdir/*
do

fn=$(basename "$f")
echo "gzip -9 "$fn

gzip -9 $f

done
