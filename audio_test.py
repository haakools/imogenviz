from pyo import *
import time
import os

# Suppress ALSA error messages
os.environ['ALSA_OUTPUT_STDERR'] = '0'

# user specific configs that would need to be set depending on your audio setup
SAMPLING_RATE=48000
OUTPUT_DEVICE=7
N_CHANNELS=2
BUFFERSIZE=512
DUPLEX=0

s = Server(sr=SAMPLING_RATE, duplex=DUPLEX, buffersize=512, nchnls=N_CHANNELS, audio='pa')

pa_list_devices()
s.setOutputDevice(OUTPUT_DEVICE)

try:
    s.boot()
    s.start()
    
    sine = Sine(freq=440, mul=0.5)
    stereo = Mix(sine, voices=2).out()

    

    
    print("Playing a 440 Hz sine wave in stereo for 5 seconds...")
    time.sleep(5)
    
    # Clean up
    a.stop()
    s.stop()
    s.shutdown()
    print("Done.")
except Exception as e:
    print(f"Error: {e}")

