import numpy as np
import matplotlib.pyplot as plt

def DFT_slow(x):
    '''compute the discrete fourier transform of the 1d array x'''
    x = np.asarray(x, dtype=float)
    N = x.shape[0]
    n = np.arange(N)
    k = n.reshape((N, 1))
    M = np.exp(-2j * np.pi * k * n / N)
    return np.dot(M, x)

'''frequency'''
# make an array of frequencies and possibly magnitudes
x = 4

START = 0
END = 10
LENGTH = 100
STEP = (END-START)/LENGTH
x1 = np.arange(START, END, STEP)
#plt.plot(x1, DFT_slow(x))
#plt.show()
#print(DFT_slow(x))

fig = plt.figure()
ax = fig.add_subplot(111)

while True:
    z = np.zeros(LENGTH)
    z[x] = 1

    ax.clear()
    #ax.plot(x1, DFT_slow(z))


    f = [0,1,0,0,0,0,0,0]
    t = [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75]
    ax.plot(t, DFT_slow(f))
    plt.show()
