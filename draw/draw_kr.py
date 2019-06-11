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
 
def main():
    x = []
    y0 = []
    y1 = []
    y2 = []
    y3 = []
    y4 = []
    y5 = []
    y6 = []
    with open(in_filename) as input_file:
        lines = input_file.read().splitlines()
    found = 0
    for line in lines:
        if line=="komi 0 1 2 3 4 5" or line=="komi s0 s1 s2 s3 s4 s5" or line=="komi s0 s1 s2 s3 s4 s5 s6 s7 s8 s9":
            found = 1
            print "found komi history"
            continue
        if found==1:
            num = line.split(' ')
            if len(num) > 2:
                n = np.array(num[:]).astype(np.float32)
                x.append(n[0])
                y0.append(n[1])
                y1.append(n[2])
                y2.append(n[3])
                y3.append(n[4])
                y4.append(n[5])
                y5.append(n[6])
    input_file.close()

    if found==0:
        print "not found komi history"
        return

    # color refer: https://www.cnblogs.com/darkknightzh/p/6117528.html
    plt.figure()
    plt.plot(x,y0, "red", label="1 black stone")
    plt.plot(x,y1, "orange", label="2 black stone")
    plt.plot(x,y2, "fuchsia", label="3 black stone")
    plt.plot(x,y3, "lawngreen", label="4 black stone")
    plt.plot(x,y4, "blue", label="5 black stone")
    plt.plot(x,y5, "blueviolet", label="6 black stone")

    x_tmp = np.array(x)
    y6 = 1/(1+np.exp(-x_tmp/10))
    plt.plot(x,y6, "black", linestyle=':', label="sigmoid")

    plt.axhline(0.5)

    plt.axvline(0)
    #plt.axvline(7.5)

    plt.legend(loc='best')
    t1name = in_filename.split('/')
    t2name = t1name[len(t1name)-1].split('_')
    print t2name[0]
    plt.title(t2name[0]+"-komi-white-winrate")
    plt.xlabel('komi')
    plt.ylabel('winrate')

    plt.savefig(t2name[0]+".png")
    plt.show()

if __name__ == "__main__":
    main()
