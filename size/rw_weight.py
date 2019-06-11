# -*- coding: utf-8 -*-
import sys
import numpy as np
import matplotlib.pyplot as plt

if len(sys.argv)==1:
    print "weight tools - still under developing"
    print "usage:"
    print "python rw_weight.py original_weight"
    sys.exit()

in_filename = sys.argv[1]
#in_filter = 256 # no.3 line's number
in_filter = -1
#in_block = 40 # when read filter*2, it's first line of policy head
in_block = -1

orig_bdsz = -1
sqr_bdsz = -1
dbl_sqr_bdsz = -1

#out_block = in_block
#out_filter = in_filter
out_bdsz = 19
out_filename = in_filename+"."+str(out_bdsz)

lines_version  = 1
lines_input    = 4
lines_residual = -1
lines_policy   = 6
lines_value    = 8

line_policy_inout = -1
line_policy_prod  = -1
line_value_inout  = -1

in_fd  = open(in_filename)
out_fd = open(out_filename, "w")

def format_n(x):
    x = float(x)
    x = '{:.3g}'.format(x)
    x = x.replace('e-0', 'e-')
    if x.startswith('0.'):
        x = x[1:]
    if x.startswith('-0.'):
        x = '-' + x[2:]
    return x

def trans_m(m, sz1, sz2, type=0):
    print "trans_m: "
    s = slice(8, 9, 1)
    t = m[s,s]
    print "9,9: ", t

    s = slice(0, sz1, 1)
    t = m[s,s]

    return t

def main():
    global in_filter, in_block
    global lines_residual, line_policy_inout, line_policy_prod, line_value_inout
    global orig_bdsz, sqr_bdsz, dbl_sqr_bdsz

    no = 1
    while 1:
        line = in_fd.readline()

        num = line.split()

        if no == 3:
            #print "no: ", no, len(num)
            print "filter: ", len(num)
            in_filter = len(num)
        if len(num) == 2*in_filter:
            #print "no: ", no, len(num)
            print "block:  ", (no-6)/8
            in_block = (no-6)/8
            lines_residual = 2*in_block*4
            line_policy_inout = lines_version + lines_input + lines_residual + 5
            line_policy_prod  = lines_version + lines_input + lines_residual + 6
            line_value_inout  = lines_version + lines_input + lines_residual + lines_policy + 5

        # 362 x (361, 361)
        if no == line_policy_inout:
            print "no: ", no, len(num)
            x = len(num)/2
            y = np.sqrt((np.sqrt(1+4*x)-1)/2)
            orig_bdsz = int(y)
            sqr_bdsz = orig_bdsz * orig_bdsz
            dbl_sqr_bdsz = 2*sqr_bdsz
            print "boardsize: ", orig_bdsz
            print in_filename, orig_bdsz, " -> ", out_filename 
            print "keyline:", line_policy_inout, line_policy_prod, line_value_inout
            print
            print "policy-inout (", sqr_bdsz, "+1) x (", sqr_bdsz, "^2)" 
            tmp_m1 = np.array(num[0:sqr_bdsz*dbl_sqr_bdsz]).astype(np.float64)
            tmp_m2 = tmp_m1.reshape(orig_bdsz, orig_bdsz, 2, orig_bdsz, orig_bdsz)
            #print "tmp_m2: ", tmp_m2[8][8][0][8][8], tmp_m2[8][8][1][8][8]
            mt = []
            for i in range(0, sqr_bdsz+1):
                begin1 = i * dbl_sqr_bdsz
                end1 = begin1 + sqr_bdsz
                end2 = begin1 + dbl_sqr_bdsz
                m1 = np.array(num[begin1:end1]).astype(np.float32)
                m2 = np.array(num[end1  :end2]).astype(np.float32)
                #print i+1, ": ", begin1, " ~ ", end1, " ~ ", end2, len(m1), m1[0], m1[sqr_bdsz], len(m2), m2[0], m2[sqr_bdsz]

                #draw
                x = m1.reshape(orig_bdsz, orig_bdsz)
                title_name=in_filename+"-policy_inout1-"+format("%03d" % i)
                plt.imshow(x, cmap=plt.cm.Reds)
                plt.colorbar()
                plt.title(title_name)
                #plt.show() 
                plt.savefig(title_name+".png")
                plt.clf()

                x = m2.reshape(orig_bdsz, orig_bdsz)
                title_name=in_filename+"-policy_inout2-"+format("%03d" % i)
                plt.imshow(x, cmap=plt.cm.Reds)
                plt.colorbar()
                plt.title(title_name)
                #plt.show() 
                plt.savefig(title_name+".png")
                plt.clf()

                m = []
                m.append(m1)
                m.append(m2)
                mt.append(m)
            #print "mt: ", len(mt), len(mt[0]), len(mt[0][0])
            print

        # 1 x (361, 1)
        if no == line_policy_prod:
            print "no: ", no, len(num)
            print "policy-innerproduct 1x(", sqr_bdsz, ",1)"
            print "4b32f should:      -0.83486116 -0.4850161 -0.05133139 -0.22740546 3.5049376"
            print "num:               0,          1,         359,        360,        361"
            print "num:              ", num[0], num[1], num[sqr_bdsz-2], num[sqr_bdsz-1], num[sqr_bdsz]
            for i in range(0,1):
                begin = i * sqr_bdsz
                end = begin + sqr_bdsz
                m = np.array(num[begin:end]).astype(np.float64)
                m = m.reshape(orig_bdsz, orig_bdsz)

                #draw
                x = m
                title_name=in_filename+"-policy_prod-"+format("%03d" % i)
                plt.imshow(x, cmap=plt.cm.Reds)
                plt.colorbar()
                plt.title(title_name)
                #plt.show() 
                plt.savefig(title_name+".png")
                plt.clf()

            ps = num[end]
            print "actual:            0,0         0,1        18,17,      18,18       19,19"
            print "actual:           ", m[0][0], m[0][1], m[orig_bdsz-1][orig_bdsz-2], m[orig_bdsz-1][orig_bdsz-1], ps
            n0 = map(format_n, m[0])
            n18 = map(format_n, m[orig_bdsz-1])
            print "actual(quantize): ", n0[0], n0[1], n18[orig_bdsz-2], n18[orig_bdsz-1]

            # transfer to
            n = trans_m(m, orig_bdsz, out_bdsz)
            n = n.reshape(sqr_bdsz)
            l = list(n)

            line = ' '.join(map(str, l)) + ' ' + ps
            print

        # 256 x (361)
        if no == line_value_inout:
            print "no: ", no, len(num)
            print "value head ", in_filter, "x", sqr_bdsz
            tmp_m1 = np.array(num).astype(np.float64)
            tmp_m2 = tmp_m1.reshape(256, orig_bdsz, orig_bdsz)
            #print "tmp_m2[0].size .ndim ", tmp_m2[0].size, tmp_m2[0].ndim

            mt = []
            for i in range(0,256):
                #draw
                x = tmp_m2[i].reshape(orig_bdsz, orig_bdsz)
                title_name=in_filename+"-valuehead-"+format("%03d" % i)
                plt.imshow(x, cmap=plt.cm.Reds)
                plt.colorbar()
                plt.title(title_name)
                #plt.show() 
                plt.savefig(title_name+".png")
                plt.clf()

                begin = i * sqr_bdsz
                end = begin + sqr_bdsz
                m = np.array(num[begin:end]).astype(np.float64)
                #print i+1, ": ", begin, " ~ ", end, len(m), m[0], m[sqr_bdsz-1]
                mt.append(m)

            #print "mt: ", len(mt), len(mt[0])
            print

        # output to file
        out_fd.write(line)

        no += 1
        if not line:
            break
        pass

    in_fd.close()
    out_fd.close()

if __name__ == "__main__":
    main()
