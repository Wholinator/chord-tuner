import scipy.io.wavfile
import matplotlib.pyplot as plt
import numpy as np

rate, data = scipy.io.wavfile.read('files\Guit_44.1k_32b_None.wav')

t = (np.fft.fft(data))

X = np.linspace(0, len(t), len(t))

plt.plot(X, t)
plt.plot(X, data)
plt.show()
