import numpy as np
import matplotlib.pyplot as plt
import keyboard as key, time

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
LENGTH = 500
STEP = (END-START)/LENGTH
x1 = np.arange(START, END, STEP)

z = np.zeros(LENGTH)
z[x] = 1

plt.ion()
fig = plt.figure()
fig.set_size_inches(18.5, 10.5)
ax = fig.add_subplot(111)
line1, = ax.plot(x1, DFT_slow(z), 'r-')

while True:
    if key.is_pressed('up') and x < LENGTH-1:
        x += 1
        z = np.zeros(LENGTH)
        z[x] = 1
        line1.set_ydata(DFT_slow(z))
        fig.canvas.draw()
        fig.canvas.flush_events()
    if key.is_pressed('down') and x > 1:
        x -= 1
        z = np.zeros(LENGTH)
        z[x] = 1
        line1.set_ydata(DFT_slow(z))
        fig.canvas.draw()
        fig.canvas.flush_events()
    if key.is_pressed('esc'):
        exit(0)

    print(x)
    plt.show()
    # time.sleep(3)
