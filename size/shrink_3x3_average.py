# -*- coding: utf-8 -*-
import numpy as np

print "__name__: ", __name__

def shrink(a, sz=9):
    out_num = sz-1
    sz_out = []
    b = []
    for n in range(0, out_num):
        sz_out.append(sz - (n+1))
        b.append(np.zeros(sz_out[n]*sz_out[n]).reshape(sz_out[n], sz_out[n]))

    for n in range(0, out_num):
        for i in range(0, sz_out[n]):
            for j in range(0, sz_out[n]):
                t = n+2
                total = 0
                for k1 in range(i, i+t):
                    for k2 in range(j, j+t):
                        total += a[k1][k2]
                b[n][i][j] = total/(t*t)

    print "a:\n", a
    print 'std: ', a.std(), 'sum: ', a.sum(), 'mean: ', a.mean()
    for n in range(0, out_num):
        if (sz_out[n] == (sz-2)):
            print '\nb[%d]:' % n
            print 'size: ', sz_out[n], 'std: ', b[n].std(), 'sum: ', b[n].sum(), 'mean: ', b[n].mean()
            print 'argmax: ', b[n].argmax()
            print b[n]

if __name__ == "__main__":
    print 'shrink 19x19 to 17x17 by using 3x3 average:\n'
    size = 9
    a = np.arange(size*size).reshape(size, size)
    shrink(a, size)

