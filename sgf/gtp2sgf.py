# -*- coding: utf-8 -*-
import sys
import numpy as np
import matplotlib.pyplot as plt

if len(sys.argv)==1:
    print "GTP tools - transfer gtp print to sgf"
    print "Usage:"
    print "python gtp2sgf gtp_print filename.sgf"
    sys.exit()

in_filename = sys.argv[1]
print len(sys.argv)
if len(sys.argv)==3:
    out_filename = sys.argv[2]
else:
    out_filename = ""
sgf_str = "(;CA[UTF-8]GM[1]FF[4]AP[Webgo]ST[2]DT[20190531]\n"\
        "PW[OZ14]WR[9p]PB[157-p300]BR[9p]\n"\
        "SZ[19]KM[0.0]RU[Chinese]OT[3x60 byo-yomi]\n"\
        ";B[pd];W[];B[dp];W[];B[dd];W[];B[pp]\n"
sgf_comment=""
 
def main():
    global sgf_comment
    with open(in_filename) as input_file:
        lines = input_file.read().splitlines()
    last_move = ""
    for line in lines:
        num = line.split()
        found = 0
        str_move = ""
        color = -1
        sgf_comment += num[0]+" "+num[1]+" "+num[2]+" "+num[4].split(')')[0]+" "+num[8].split(')')[0]+"\n"
        for move in num:
            if move=="PV:":
                found = 1
                continue
            if found == 1:
                if len(move)==0: break
                x = 'ABCDEFGHJKLMNOPQRSTUVWXYZ'.find(move[0])
                y = 19 - int(move[1:])
                #print move, ' -> ', x,y, ' -> ', 'abcdefghijklmnopqrstuvwxyz'[x], 'abcdefghijklmnopqrstuvwxyz'[y]
                if color == -1:
                    str_move += ";W[" + 'abcdefghijklmnopqrstuvwxyz'[x] + 'abcdefghijklmnopqrstuvwxyz'[y] + "]"
                    color = 1
                else:
                    str_move += ";B[" + 'abcdefghijklmnopqrstuvwxyz'[x] + 'abcdefghijklmnopqrstuvwxyz'[y] + "]"
                    color = -1
        if last_move=="":
            last_move = str_move
        else:
            last_move = "("+last_move+")\n" + str_move
    input_file.close()
    print sgf_comment
    print sgf_str + "C[" + sgf_comment + "]" + last_move + ")"
    if len(out_filename)!=0:
        out_fd = open(out_filename, "w")
        out_fd.write(sgf_str + "C[" + sgf_comment + "]" + last_move + ")")
        out_fd.close()

if __name__ == "__main__":
    main()
