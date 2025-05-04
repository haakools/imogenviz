
from pyo import *
import time

# Suppress ALSA error messages
os.environ['ALSA_OUTPUT_STDERR'] = '0'

# Global audio configuration (same as before)
SAMPLING_RATE = 48000
OUTPUT_DEVICE = 10
N_CHANNELS = 2
BUFFERSIZE = 512
DUPLEX = 0
AUDIO="alsa"
pa_list_devices()



def setup_server():
    server = Server(
        sr=SAMPLING_RATE,
        duplex=DUPLEX,
        buffersize=BUFFERSIZE,
        nchnls=N_CHANNELS,
        audio=AUDIO
    )
    server.setOutputDevice(OUTPUT_DEVICE)
    server.boot()
    server.start()
    return server


def close_server(server):
    server.stop()
    server.shutdown()

