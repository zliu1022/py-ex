# -*- coding: utf-8 -*-
import sys
import numpy as np
import matplotlib.pyplot as plt

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
                print "Draw Game", found
                align_data()
                #if found==21: 
                draw_plot()
                x = []
                y0 = []
                y1 = []
                y2 = []
                #if found==2: return
            found += 1
            print "found Game", num[1], found
            continue
        if found<>0:
            if len(num)<6:
                continue
            #print num
            if num[0]=="Zen7-0.4":
                #print num
                x.append(int(num[3]))
                y0.append(float(num[7].strip('%')))
                continue
            if num[0][0:8]=="0.17-157":
                #print num
                y1.append(float(num[7].strip('%')))
                continue
            if num[0]=="Zen7-0.4-Referee":
                #print num
                if num[1]=="B":
                    if num[5][0]=="B":
                        y2.append(float(num[5][1:]))
                    else:
                        y2.append(-1.0*float(num[5][1:]))
                continue
    if found==0:
        print "not found Game"
        return
    align_data()
    draw_plot()

def draw_plot():
    global x,y0,y1,y2
    global found

    plt.figure()
    plt.plot(x,y0, "red", label="Zen7-s15000")
    plt.plot(x,y1, "blue", label="157-p300")
    plt.plot(x,y2, "black", label="score")

    plt.axhline(50)
    plt.axhline(90)
    plt.axhline(10)

    plt.axvline(0)

    plt.legend(loc='best')
    t1name = in_filename.strip(".log")
    print "t1name: ", t1name
    print found
    t2name = t1name + ("-%d" % (found-1))
    print "t2name: ", t2name
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
        print "len> align y1: ", len(x), len(y0), len(y1)
    if len(y1)<len(x):
        delta = len(x) - len(y1)
        last_y1 = y1[len(y1)-1]
        for i in range(0,delta):
            y1.append(last_y1)
        print "len< align y1: ", len(x), len(y0), len(y1)
    
    if len(y2)>len(x):
        delta = len(y2) - len(x)
        for i in range(0,delta):
            y2.pop()
        print "len> align y2: ", len(x), len(y0), len(y1), len(y2)
    if len(y2)<len(x):
        delta = len(x) - len(y2)
        last_y2 = y2[len(y2)-1]
        for i in range(0,delta):
            y2.append(last_y2)
        print "len< align y2: ", len(x), len(y0), len(y1), len(y2)


if __name__ == "__main__":
    main()
