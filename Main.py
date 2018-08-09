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


def init_plot(x):
    global line1, fig

    # generate x values for plotting
    x1 = np.arange(START, END, STEP)

    # create input array for DFT
    z = np.zeros(PARAMS)
    z[x] = 1

    #initialize plot
    plt.ion()
    #plt.axis('scaled')
    fig = plt.figure()
    fig.set_size_inches(18.5, 10.5)
    ax = fig.add_subplot(111)

    # produce y values and lengthen to required set for plotting
    output = DFT_slow(z)
    output = resize_output(len(x1), output)

    # initialize line object for plotting and updating
    line1, = ax.plot(x1, output, 'r-')
    plt.show()


# repeat data to fill up desired space
def resize_output(size, arr):
    f_out = arr

    while size > len(f_out) + len(arr):
        f_out = np.concatenate((f_out, arr))

    diff = size - len(f_out)

    if diff > 0:
        f_out = np.concatenate((f_out, arr[0:diff]))

    return f_out


def update_plot(arr, i, change):
    arr[i] += change

    output = DFT_slow(arr)
    output = resize_output(POINTS, output)
    line1.set_ydata(output)
    fig.canvas.draw()
    fig.canvas.flush_events()
    return arr


#
# Init Graph
#
x = 1
START = 0
END = 250
POINTS = 500
PARAMS = 10
STEP = (END-START)/POINTS
line1 = None
fig = None
init_plot(x)

z = np.zeros(PARAMS)

while True:
    if key.is_pressed('up') and x < PARAMS-1:
        x += 1
        #update_plot(z, x, 1)
        z = np.zeros(PARAMS)
        z[x] = 1
        line1.set_ydata(resize_output(POINTS, DFT_slow(z)))
        fig.canvas.draw()
        fig.canvas.flush_events()
    if key.is_pressed('down') and x > 1:
        x -= 1
        #update_plot(z, x, -1)
        z = np.zeros(PARAMS)
        z[x] = 1
        line1.set_ydata(resize_output(POINTS, DFT_slow(z)))
        fig.canvas.draw()
        fig.canvas.flush_events()
    if key.is_pressed('esc'):
        exit(0)

    print(x)
    plt.show()
    # time.sleep(3)
