#!/bin/bash
currentdir=./
#lzdir=/home/zliu1022/go
lzdir=/Users/zliu/go/leela-zero

po=1200
thread=2

for f in $currentdir/*.gz
do
echo $f
cat gtp_h4_k0 | $lzdir/leelaz-dual -g -w $f -p$po --noponder --komi 50 -r0.1 -t$thread
cat gtp_h4_k0 | $lzdir/leelaz-dual -g -w $f -p$po --noponder --komi 55 -r0.1 -t$thread
cat gtp_h4_k0 | $lzdir/leelaz-dual -g -w $f -p$po --noponder --komi 60 -r0.1 -t$thread
cat gtp_h4_k0 | $lzdir/leelaz-dual -g -w $f -p$po --noponder --komi 65 -r0.1 -t$thread
cat gtp_h4_k0 | $lzdir/leelaz-dual -g -w $f -p$po --noponder --komi 70 -r0.1 -t$thread
cat gtp_h4_k0 | $lzdir/leelaz-dual -g -w $f -p$po --noponder --komi 75 -r0.1 -t$thread
cat gtp_h4_k0 | $lzdir/leelaz-dual -g -w $f -p$po --noponder --komi 80 -r0.1 -t$thread
cat gtp_h4_k0 | $lzdir/leelaz-dual -g -w $f -p$po --noponder --komi 85 -r0.1 -t$thread
cat gtp_h4_k0 | $lzdir/leelaz-dual -g -w $f -p$po --noponder --komi 90 -r0.1 -t$thread
cat gtp_h4_k0 | $lzdir/leelaz-dual -g -w $f -p$po --noponder --komi 95 -r0.1 -t$thread
done

#./OZ-tree_bat.sh > OZ-tree.out 2>&1
