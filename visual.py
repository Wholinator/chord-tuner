import math
import my_wave as wave
import pyaudio
import itertools

pya = pyaudio.PyAudio()

f = wave.open('drum.wav')

# initialize our stream
sampwidth = f.getsampwidth()
nchannels = f.getnchannels()
framerate = f.getframerate()
out_stream = pya.open(format = pya.get_format_from_width(width=sampwidth), channels=nchannels, rate=framerate, output=True)


def compress_sorta(stream, threshold=75, ratio=2):
    full_bytes = []

    for chunk in stream:
        new_chunk = []
        for byte in chunk:
            x = int(byte) - 128
            y = x
            if x > threshold:
                y = ((x - threshold) / ratio) + threshold
            new_chunk.append(int(y) + 128)
        full_bytes.append(bytes(new_chunk))

    return full_bytes


def rolling_average(stream):
    full_bytes = []
    old_byte = 0

    for chunk in stream:
        new_chunk = []
        for byte in chunk:
            y = (old_byte + byte) / 2
            new_chunk.append(int(y))
            old_byte = byte
        full_bytes.append(bytes(new_chunk))

    return full_bytes


def divide_by_2(stream):
    full_bytes = []

    for chunk in stream:
        new_chunk = []
        for byte in chunk:
            x = int(byte) - 128
            y = int(x / 2)
            new_chunk.append(y + 128)
        full_bytes.append(bytes(new_chunk))

    return full_bytes


def audio_generator(buffer, f):
    stream = [f.readframes(buffer) for i in range(0, math.ceil(f.getnframes() / buffer))]

    stream = compress_sorta(stream)
    # stream = rolling_average(stream)
    # stream = divide_by_2(stream)
    
    while stream:
        for chunk in stream:
            yield chunk

def play_stream(stream, gen):
    for chunk in gen:
        stream.write(chunk)





gen = audio_generator(2048, f)
play_stream(out_stream, gen)
