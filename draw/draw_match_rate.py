# -*- coding: utf-8 -*-
import sys
import numpy as np
import matplotlib.pyplot as plt
import os

if len(sys.argv)!=2:
    print "komi tools - draw_kr.py : draw komi-rate curve"
    print "Usage: "
    print "cat gtp_0 | ~/go/leela-zero/leelaz-dual-se -g --cpu-only -w ~/go/weights/4x32/4b32f.gz > 4b32_kr 2>&1"
    print "python draw_kr.py 4b32f_kr"
    sys.exit()

in_filename = sys.argv[1]
 
x = []
y0 = []
y1 = []
y2 = []
found = 0

#0.17-4b32f()0(7.5 46.67%) B No.   1 0.0s Q16    86 46.6682% 22.86%
#player1_label="Zen7-0.4"
player1_label="0.17-4b32f()0(7.5"

#0.17-4b_76000()0(7.5 54.24%) W No.   2 0.1s  D4   143 54.2417% 40.78%
#player2_label="0.17-157"
player2_label="0.17-186000()0(7.5"

def main():
    global x,y0,y1,y2
    global found

    with open(in_filename) as input_file:
        lines = input_file.read().splitlines()
    input_file.close()

    found = 0
    for line in lines:
        #num = line.split(' ')
        num = line.split()
        if len(num) <=0: continue
        if num[0]=="Game":
            if found<>0:
                #print "Draw Game", found-1
                align_data()
                #if found==21: 
                draw_plot()
                x = []
                y0 = []
                y1 = []
                y2 = []
                #if found==2: return
            found += 1
            print "Game", num[1]
            continue
        if found<>0:
            if len(num)<6:
                continue
            #print num
            if num[0]==player1_label:
                #print num
                x.append(int(num[4]))
                y0.append(float(num[8].strip('%')))
                continue
            if num[0]==player2_label:
                #print num
                if (len(num[8])>=7):
                    y1.append(float(num[8].strip('%')))
                else:
                    y1.append(y1[len(y1)-1])
                continue
            if num[0]=="Zen7-0.4-Referee":
                #print num
                if num[1]=="B":
                    if num[5][0]=="B":
                        if found%2<>0:
                            y2.append(50.0+float(num[5][1:]))
                        else:
                            y2.append(50.0-1.0*float(num[5][1:]))
                    else:
                        if found%2<>0:
                            y2.append(50.0-1.0*float(num[5][1:]))
                        else:
                            y2.append(50.0+float(num[5][1:]))
                continue
    if found==0:
        print "not found Game"
        return
    align_data()
    draw_plot()

def draw_plot():
    global x,y0,y1,y2
    global found

    bname = os.path.basename(in_filename)
    dirname = os.path.dirname(in_filename)
    t1name = bname.strip(".log")
    #print "t1name: ", t1name
    player1 = t1name[0: t1name.find("_v_",0)]
    player2 = t1name[t1name.find("_v_",0)+3: bname.find("-200",0)]
    #print player1, player2
    #print found
    if dirname == '':
        dirname = '.'
    t2name = dirname + "/" + t1name + ("-%d" % (found-1))
    #print "t2name: ", t2name

    plt.figure()
    plt.plot(x,y0, "red", label=player2)
    plt.plot(x,y1, "blue", label=player1)
    #plt.plot(x,y2, "green", label="score")

    plt.axhline(50)
    plt.axhline(90)
    plt.axhline(10)

    plt.axvline(0)

    plt.legend(loc='best')
    plt.title(t2name)
    plt.xlabel('move')
    plt.ylabel('winrate')

    plt.savefig(t2name+".png")
    #plt.show()
    plt.close()

def align_data():
    global x,y0,y1,y2
    print "len(x,y0,y1,y2): ", len(x), len(y0), len(y1), len(y2)
    if len(y1)>len(x):
        delta = len(y1) - len(x)
        for i in range(0,delta):
            y1.pop()
        #print "len> align y1: ", len(x), len(y0), len(y1)
    if len(y1)<len(x):
        delta = len(x) - len(y1)
        last_y1 = y1[len(y1)-1]
        for i in range(0,delta):
            y1.append(last_y1)
        #print "len< align y1: ", len(x), len(y0), len(y1)
    
    if len(y2)>len(x):
        delta = len(y2) - len(x)
        for i in range(0,delta):
            y2.pop()
        #print "len> align y2: ", len(x), len(y0), len(y1), len(y2)
    if len(y2)<len(x) and len(y2)!=0:
        delta = len(x) - len(y2)
        last_y2 = y2[len(y2)-1]
        for i in range(0,delta):
            y2.append(last_y2)
        #print "len< align y2: ", len(x), len(y0), len(y1), len(y2)


if __name__ == "__main__":
    main()
