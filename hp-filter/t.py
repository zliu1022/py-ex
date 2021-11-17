import numpy as np
import matplotlib.pyplot as plt
#import matplotlib
import pandas as pd
from scipy import sparse, stats

def hp(y, lamb=10):
    def D_matrix(N):
        D = np.zeros((N-1,N))
        D[:,1:] = np.eye(N-1)
        D[:,:-1] -= np.eye(N-1)
        """D1
        [[-1.  1.  0. ...  0.  0.  0.]
         [ 0. -1.  1. ...  0.  0.  0.]
         [ 0.  0. -1. ...  0.  0.  0.]
         ...
         [ 0.  0.  0. ...  1.  0.  0.]
         [ 0.  0.  0. ... -1.  1.  0.]
         [ 0.  0.  0. ...  0. -1.  1.]]
        """
        return D
    N = len(y)
    D1 = D_matrix(N)
    D2 = D_matrix(N-1)
    D = D2 @ D1
    g = np.linalg.inv((np.eye(N)+lamb*D.T@D))@ y
    return g

def mad(data, axis=None):
    return np.mean(np.abs(data - np.mean(data, axis)), axis)

def AnomalyDetection(x, alpha=0.2, lamb=5000):
    """
    x         : pd.Series
    alpha     : The level of statistical significance with which to
                accept or reject anomalies. (expon distribution)
    lamb      : penalize parameter for hp filter
    return r  : Data frame containing the index of anomaly
    """
    # calculate residual
    xhat = hp(x, lamb=lamb)
    resid = x - xhat

    # drop NA values
    ds = pd.Series(resid)
    ds = ds.dropna()

    # Remove the seasonal and trend component,
    # and the median of the data to create the univariate remainder
    md = np.median(x)
    data = ds - md

    # process data, using median filter
    ares = (data - data.median()).abs()
    data_sigma = data.mad() + 1e-12
    ares = ares/data_sigma

    # compute significance
    p = 1. - alpha
    R = stats.expon.interval(p, loc=ares.mean(), scale=ares.std())
    threshold = R[1]

    # extract index, np.argwhere(ares > md).ravel()
    r_id = ares.index[ares > threshold]

    return r_id

'''
N = 1024
#t = np.linspace(1, 2*np.pi, N)
t = np.linspace(1, 10, N)
y = np.sin(t) + np.cos(20*t) + np.random.randn(N)*0.1
'''
np.random.seed(42)
N = 1024  # number of sample points
t = np.linspace(0, 2*np.pi, N)
y = np.sin(t) + 0.02*np.random.randn(N)

plt.figure(figsize=(10,12))
#for i,l in enumerate([0.1,1,10,100,1000, 10000]):
for i,l in enumerate([0.1, 10, 1000, 5000]):
    plt.subplot(3,2,i+1)
    g = hp(y,l)
    r_idx = AnomalyDetection(y, alpha=0.1, lamb=l)
    plt.plot(y, label='original')
    plt.plot(g, label='filtered')
    plt.plot(r_idx, y[r_idx], 'ro')
    plt.legend()
    plt.title('$\lambda$='+str(l))
plt.show()

