import sys
import my_wave as wave
import math
import struct
import random
import argparse
import pyaudio
import PySimpleGUI as sg
from itertools import count, cycle, islice, zip_longest

# from here https://zach.se/generate-audio-with-python/
# python -u "/Users/mwholey/Documents/git_repos/chord-tuner/Main.py"

def clip_amplitude(amplitude):
  return float(1.0 if amplitude > 1.0 else 0.0 if amplitude < 0.0 else amplitude)

def sin_wave_old(frequency=440.0, samplerate=44100, amplitude=0.5):
  amplitude = clip_amplitude(amplitude)
  angular_frequency = 2.0 * math.pi * float(frequency)
  sin_generator = (float(amplitude) * math.sin(angular_frequency * (float(i) / float(samplerate))) for i in count(0))
  return sin_generator

# computes a sin wave for the period of the wave, then returns the infinite generator of that period looped
# can think of this as computing the y value for a given x
# the x is the generator of the i/samplerate for i in period 
def sin_wave(frequency=440.0, samplerate=44100, amplitude=0.5):
  period = int(samplerate / frequency)
  amplitude = clip_amplitude(amplitude)
  lookup = [float(amplitude) * math.sin(2.0*math.pi*float(frequency)*(float(i%period)/float(samplerate))) for i in range(period)]
  return (lookup[i%period] for i in count(0))


  
# returns random value generator
def white_noise_generator(amplitude=0.5):
  return (clip_amplitude(amplitude) * random.uniform(-1, 1) for _ in count(0))


def white_noise(amplitude=0.5):
  noise = cycle(islice(white_noise_generator(amplitude), 44100))
  return noise


def compute_samples(channels, nsamples=None):
  # zip(*channel) this combines all the channel components into a single channel list with tuples for each timeslice containing each component
  # map(sum, zip(*channel)) for channel in channels - this sums all the channel components into a single list for each channel
  # zip(*(map...)) takes the channel audio streams, and combines them into a single stream of tuples one element for each original channel
  # islice cuts this infinite stream at the sample size desired
  return islice(zip(*(map(sum, zip(*channel)) for channel in channels)), nsamples)


def grouper(n, iterable, fillvalue=None):
  args = [iter(iterable)] * n
  return zip_longest(fillvalue=fillvalue, *args)

def write_wavefile(filename, samples, nframes=44100, nchannels=2, sampwidth=2, framerate=44100, bufsize=2048):


  w = wave.open(filename, 'w')
  w.setparams((nchannels, sampwidth, framerate, nframes, 'NONE', 'not compressed'))

  max_amplitude = float(int((2 ** (sampwidth * 8)) / 2) - 1)

  totalbuf = 0
  for chunk in grouper(bufsize, samples):
    totalbuf += bufsize
    if totalbuf > 200000:
      break
    frames = b''.join(b''.join(struct.pack('h', int(max_amplitude * sample)) for sample in channels) for channels in chunk if channels is not None)
    w.writeframesraw(frames)

  w.close()

  return filename

def write_audiostream(samples, nframes=44100, nchannels=2, sampwidth=2, framerate=44100, bufsize=2048):
  pya = pyaudio.PyAudio()
  stream = pya.open(format = pya.get_format_from_width(width=sampwidth), channels=nchannels, rate=framerate, output=True)

  max_amplitude = float(int((2 ** (sampwidth * 8)) / 2) - 1)

  for chunk in grouper(bufsize, samples):
    frames = b''.join(b''.join(struct.pack('h', int(max_amplitude * sample)) for sample in channels) for channels in chunk if channels is not None)
    stream.write(frames)


def main():
  channels=(
            (sin_wave(frequency=220.0),sin_wave(frequency=440.0)), # left channel
            (sin_wave(frequency=220.0),sin_wave(frequency=440.0))  # right channel
           )
  samples = compute_samples(channels)

  filename = sys.stdout
  # filename = 'test.wav'

  #write_wavefile(filename, samples)
  #write_audiostream(samples)

  ### GUI
  layout = [
    [sg.Text('Oscilator 1'), sg.Slider(range=(20.0,500.0),default_value=440.0,orientation='h'), sg.Slider(range=(0.0,1.0),default_value=0.5,resolution=0.01,orientation='h')],
    [sg.InputText()],
    [sg.Output(size=(250,50))],
    [sg.Submit(), sg.Cancel()]
  ]

  window = sg.Window('Shit', layout)

  while True:
    event, values = window.read()
    print(event,values)
    if event in (None, 'Exit', 'Cancel'):
      break
  

main()