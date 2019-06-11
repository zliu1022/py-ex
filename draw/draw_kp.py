# -*- coding: utf-8 -*-
import sys
import numpy as np
import matplotlib.pyplot as plt
import os
import imageio

'''
x = np.random.rand(10, 10)
plt.matshow(x, cmap = plt.cm.cool, vmin=0, vmax=1)
plt.colorbar()
plt.show()
x = np.random.rand(100).reshape(10,10)
plt.imshow(x, cmap=plt.cm.hot, vmin=0, vmax=1)
plt.colorbar()
plt.show()
sys.exit()
'''

if len(sys.argv)!=2:
    print "komi tools - draw_kp.py : draw komi-policy gif"
    print "Usage: "
    print "cat gtp_p | ~/go/leela-zero/leelaz-dual-se -g --cpu-only -w ~/go/weights/OZ/OZ14.gz > OZ14_kp 2>&1"
    print "python draw_kp.py OZ14_kp"
    sys.exit()

in_filename = sys.argv[1]
t1name = in_filename.split('/')
t2name = t1name[len(t1name)-1].split('_')

def create_gif(source, name, duration):
    frames = []     # 读入缓冲区
    for img in source:
        if img.find(".png") == -1: continue
        print img
        tmp = imageio.imread(img)
        frames.append(tmp)
    imageio.mimsave(name, frames, 'GIF', duration=duration)

def main():
    with open(in_filename) as input_file:
        lines = input_file.read().splitlines()
    m = np.empty(shape=[0,19])
    #print m.size, m.shape, m.ndim, m.type
    found = 0
    count = 1
    total = 0
    picname = ""
    os.mkdir(t2name[0]+"-png")
    path = os.chdir(t2name[0]+"-png")
    for line in lines:
        if line.find("komi-") != -1:
            #print line
            picname = line.split(' ')[0]
            found = 1
            count = 1
            total += 1
            continue
        if found == 1:
            num = line.split()
            num = map(float, num)
            n = np.array(num)
            m = np.insert(m, 0, n, axis=0)
            count += 1
            if count == 20:
                # cmap value can refer: https://matplotlib.org/examples/color/colormaps_reference.html
                # hot, cool, Reds
                plt.imshow(m, cmap=plt.cm.Reds, vmin=m.min(), vmax=m.max())
                plt.colorbar()

                title_name = t2name[0]+"-komi-policy"+"("+picname[5:]+")"
                save_name = format("%03d" % total) + "-" + t2name[0]+"-kp"+"("+picname[5:]+")"
                print save_name
                plt.title(title_name)
                #plt.show() 
                plt.savefig(save_name+".png")
                plt.clf()

                found = 0
                m = np.empty(shape=[0,19])
                count = 1

    pic_list = os.listdir(".")
    pic_list.sort()
    gif_name = t2name[0] + "-komi-policy.gif"
    duration_time = 0.5
    create_gif(pic_list, gif_name, duration_time)

if __name__ == "__main__":
    main()

