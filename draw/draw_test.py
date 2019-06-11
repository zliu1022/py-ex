# -*- coding: utf-8 -*-
import sys
import numpy as np
import matplotlib.pyplot as plt

def main():
    x = np.arange(-20, 20, 0.1)
    y0 = 1/(1+np.exp(-x))
    y1 = (1+np.tanh(x))/2
    y2 = (1+np.tanh(x*0.25))/2
    #y3 = (1+np.tanh(x*0.904891304))/2
    #y3 = (1+np.tanh(x-1))/2

    plt.figure()
    plt.plot(x,y0, "blue", label="sigmoid")
    plt.plot(x,y1, "red", label="tanh")
    plt.plot(x,y2, "orange", label="tanh(x*0.25)")
    #plt.plot(x,y3, "blueviolet", label="tanh(x*?)")

    plt.axhline(0.5)

    plt.axhline(0.5)
    plt.axvline(0)

    plt.legend(loc='best')
    plt.title("sigmoid")
    plt.xlabel('weight-output-winrate')
    plt.ylabel('leelazero-winrate')

    #plt.savefig(t2name[0]+".png")
    plt.show()

if __name__ == "__main__":
    main()
