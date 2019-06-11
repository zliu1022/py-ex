# -*- coding: utf-8 -*-
from pylab import *
 
def f(x,y): return (1-x/2+x**5+y**3)*np.exp(-x**2-y**2)

def t_grid():
    axes = gca()
    axes.set_xlim(0,4)
    axes.set_ylim(0,3)
    axes.set_xticklabels([])
    axes.set_yticklabels([])

    show()

def t_contour():
    n = 256
    x = np.linspace(-3,3,n)
    y = np.linspace(-3,3,n)
    X,Y = np.meshgrid(x,y)

    contourf(X, Y, f(X,Y), 8, alpha=.75, cmap='jet')
    C = contour(X, Y, f(X,Y), 8, colors='black', linewidth=.5)
    show()

def t_gray():
    n = 10
    x = np.linspace(-3,3,4*n)
    y = np.linspace(-3,3,3*n)
    X,Y = np.meshgrid(x,y)
    imshow(f(X,Y)), show()

if __name__ == "__main__":
    t_gray()

