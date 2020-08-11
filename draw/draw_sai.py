# -*- coding: utf-8 -*-
import sys
import numpy as np
import matplotlib.pyplot as plt

def main():
    x = np.arange(-60, 60, 0.1)

    alpha = 0
    beta = 1
    y0 = 0.5 * np.tanh(0.5*beta*(alpha+x)) + 0.5

    alpha = 7.5
    beta = 0.11
    y1 = 0.5 * np.tanh(0.5*beta*(alpha+x)) + 0.5

    alpha = 5.5
    beta = 10 
    y2 = 0.5 * np.tanh(0.5*beta*(alpha+x)) + 0.5

    alpha = -4.0
    beta = 0.11
    y3 = 0.5 * np.tanh(0.5*beta*(alpha+x)) + 0.5

    alpha = 0
    beta = 0.11
    y4 = 0.5 * np.tanh(0.5*beta*(alpha+x)) + 0.5

    plt.figure()
    # sigmoid, empty, final
    #plt.plot(x,y0, "blue", label="sigmoid")
    #plt.plot(x,y1, "red", label="empty")
    #plt.plot(x,y2, "orange", label="final")

    # empty, lambda, mu
    plt.plot(x,y1, "blue", label="empty")
    plt.plot(x,y3, "red", label="lambda")
    plt.plot(x,y4, "orange", label="mu")

    plt.axhline(0.5)

    plt.axhline(0.5)
    plt.axvline(0)

    plt.legend(loc='best')
    plt.title("sai-komi-winrate")
    plt.xlabel('komi')
    plt.ylabel('winrate')

    plt.savefig("sai.png")
    plt.show()

if __name__ == "__main__":
    main()
