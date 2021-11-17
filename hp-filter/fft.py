# 离散时间傅里叶变换的python实现
import numpy as np
import math
import pylab as pl
import scipy.signal as signal
import matplotlib.pyplot as plt

sampling_rate=1000
t1=np.arange(0, 10.0, 1.0/sampling_rate)
#x1 =np.sin(15*np.pi*t1)
x1 = np.sin(7*np.pi*t1) + np.sin(13*np.pi*t1+0.7*np.pi) + 1.3*np.sin(17*np.pi*t1) + np.sin(23*np.pi*t1) + 0.02*np.random.randn(10*sampling_rate)

plt.figure()
plt.plot(x1)
plt.show()

# 傅里叶变换
def fft1(xx):
    # t=np.arange(0, s)
    t=np.linspace(0, 1.0, len(xx))
    f = np.arange(len(xx)/2+1, dtype=complex)
    for index in range(len(f)):
        f[index]=complex(np.sum(np.cos(2*np.pi*index*t)*xx), -np.sum(np.sin(2*np.pi*index*t)*xx))
    return f

# len(x1)
xf=fft1(x1)/len(x1)
freqs = np.linspace(0, sampling_rate/2, len(x1)/2+1)
plt.figure(figsize=(16,4))
plt.plot(freqs,2*np.abs(xf),'r--')

plt.xlabel("Frequency(Hz)")
plt.ylabel("Amplitude($m$)")
plt.title("Amplitude-Frequency curve")

plt.show()


plt.figure(figsize=(16,4))
plt.plot(freqs,2*np.abs(xf),'r--')

plt.xlabel("Frequency(Hz)")
plt.ylabel("Amplitude($m$)")
plt.title("Amplitude-Frequency curve")
plt.xlim(0,20)
plt.show()
