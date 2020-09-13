import sys
import my_wave as wave
import math
import struct
import random
import argparse
import pyaudio
import PySimpleGUI as sg
import multiprocess
import logging
from threading import Thread
from itertools import count, cycle, islice, zip_longest

mpl = multiprocess.log_to_stderr()
mpl.setLevel(logging.INFO)
multiprocess.set_start_method("spawn")

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
  ### sum function could be changed for interesting stuff


def grouper(n, iterable, fillvalue=None):
  # "grouper(3, 'ABCDEFG', 'x') --> zip_longest((A,B,C), (D,E,F), (G,x,x))"
  # creates an array of n identical elements, each is the iterable, when one iterable is used, that action is
  # replicated across all other iterables in the array as they are all actually the same memory address
  args = [iter(iterable)] * n
  # grabs first element from each iterator and places into a tuple, then second, and so on
  # however since they're all the same iterator it actually grabs first from first, second from second, and so on
  # iterating through each iterator like we were just stepping through a single array because in essence that is what we're doing
  # since zip creates a list of n-tuples, this effectively just groups the infinite generator into an infinite list of n-tuples
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

def write_audiostream(stream, samples, nchannels=2, sampwidth=2, framerate=44100, bufsize=2048):
  max_amplitude = float(int((2 ** (sampwidth * 8)) / 2) - 1) / 100

  # if compute samples has no sample length, there'll be an infinite number of chunks
  # which are bufsize length n-tuples of samples generator
  # since it's an infinite generator this means samples are continuous with no need to reset or break, just keeps chugging along infinitely
  print('test')
  for chunk in grouper(bufsize, samples):
    frames = b''.join(b''.join(struct.pack('h', int(max_amplitude * sample)) for sample in channels) for channels in chunk if channels is not None)
    stream.write(frames)


def update_samples(values):
  channel = ()
  for i in range(50):
    if f'Osc{i}Freq' in values and f'Osc{i}Vol' in values:
      # construct sound, then convert tuple to list, append our sound, back to tuple
      sound = sin_wave(frequency=values[f'Osc{i}Freq'], amplitude=values[f'Osc{i}Vol'])
      # operations cannot be combined or NoneType error
      channel = list(channel)
      channel.append(sound)
      channel = tuple(channel)

  # mono for now 
  channels = (
    channel,
    channel
  )
  return compute_samples(channels)


def main():
  num_channels = 2
  sampwidth = 2
  framerate = 44100

  pya = pyaudio.PyAudio()
  stream = pya.open(format = pya.get_format_from_width(width=sampwidth), channels=num_channels, rate=framerate, output=True)
  #init_samples = compute_samples(((sin_wave()), (sin_wave())))
  ### GUI
  layout = [
    [
      sg.Text('Oscilator 1'), 
      sg.Slider(
        key="Osc1Freq",
        range=(20.0,500.0),
        default_value=440.0,
        orientation='h'), 
      sg.Slider(
        key="Osc1Vol",
        range=(0.0,1.0),
        default_value=0.5,
        resolution=0.01,
        orientation='h')
    ],
    [
      sg.Text('Oscilator 2'), 
      sg.Slider(
        key="Osc2Freq",
        range=(20.0,500.0),
        default_value=440.0,
        orientation='h'), 
      sg.Slider(
        key="Osc2Vol",
        range=(0.0,1.0),
        default_value=0.5,
        resolution=0.01,
        orientation='h')
    ],
    [sg.Output(size=(250,50))],
    [sg.Submit(), sg.Cancel()]
  ]

  window = sg.Window('Shit', layout)

  event_old, values_old = None, None
  while True:
    event, values = window.read(timeout = 50)
    if event in (None, 'Exit', 'Cancel'):
      break

    if values_old != values:
      print(event, values)
      event_old, values_old = event, values

      samples = update_samples(values)
      # write_audiostream(stream, samples)

      if not 'audio_proc' in locals():
        audio_proc = multiprocess.Process(target=write_audiostream, args=(stream, samples), daemon=True)
        audio_proc.start()
      else:
        audio_proc.terminate()
        audio_proc = multiprocess.Process(target=write_audiostream, args=(stream, samples), daemon=True)
        audio_proc.start()


      ## THREAD think i'm getting GIL issues, getting stuck and unable to interact with the ui as the stream loop is holding on too tight
      # if not 'audio_thread' in locals():
      #   audio_thread = Thread(target=write_audiostream, args=(stream, samples))
      #   audio_thread.daemon = True
      #   audio_thread.run()
      # else:
      #   audio_thread._stop()
      #   audio_thread = Thread(target=write_audiostream, args=(stream, samples))
      #   audio_thread.daemon = True
      #   audio_thread.run()

  

main()



# a = (math.sin(i/100) for i in itertools.count(0))
#
#
##
#
#
#