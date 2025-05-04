import numpy as np
import os
from pyo import * # a bit disgusting but bleh
# pyo setup
# Suppress ALSA error messages
os.environ['ALSA_OUTPUT_STDERR'] = '0'
# user specific configs that would need to be set depending on your audio setup
SAMPLING_RATE=48000
OUTPUT_DEVICE=7
N_CHANNELS=2
BUFFERSIZE=512
DUPLEX=0

class SimpleSynthesizer:
    def __init__(self):
        # Create and configure the server properly (only once)
        self.server = Server(
                sr=SAMPLING_RATE,
                duplex=DUPLEX,
                buffersize=BUFFERSIZE,
                nchnls=N_CHANNELS,
                audio='pa'
                )
        self.server.setOutputDevice(OUTPUT_DEVICE)
        self.server.boot()
        self.server.start()
        
        # Create oscillators using the correct Pyo classes
        self.oscillators = {
            "sine": Sine(freq=440, mul=0.5).stop(),
            # Use LFO with type=1 for square (type parameter selects waveform)
            "square": LFO(freq=440, type=1, mul=0.0).stop(),
            # Use LFO with type=2 for triangle
            "triangle": LFO(freq=440, type=2, mul=0.0).stop(),
            # Use Phasor for sawtooth (the default Phasor is a ramp-up sawtooth)
            "sawtooth": Phasor(freq=440, mul=0.0).stop()
        }
        
        # Create a Mix with stereo output (voices=2)
        self.mixer = Mix(list(self.oscillators.values()), voices=2)
        
        self.filter = Biquad(self.mixer, freq=1000, q=1, type=0)
        # Output the signal
        self.filter.out()
    
    def set_oscillator(self, osc_type, active=True, amplitude=0.5):
        """Enable/disable oscillator and set its amplitude"""
        if osc_type in self.oscillators:
            if active:
                self.oscillators[osc_type].mul = amplitude
                self.oscillators[osc_type].play()
            else:
                self.oscillators[osc_type].stop()
    
    def set_frequency(self, freq):
        """Set frequency for all oscillators"""
        for osc in self.oscillators.values():
            osc.freq = freq
    
    def set_filter(self, cutoff_freq):
        """Set filter cutoff frequency"""
        self.filter.freq = cutoff_freq
    
    def play_note(self, freq, duration=0.5):
        """Play a note of specified frequency and duration"""
        self.set_frequency(freq)
        
        # Create a simple envelope
        env = Fader(fadein=0.01, fadeout=0.1, dur=duration).play()
        
        # Apply envelope to filter
        self.filter.mul = env

# List available devices before creating the synth
pa_list_devices()

# Example usage:
if __name__ == "__main__":
    # Create synth
    synth = SimpleSynthesizer()
    
    # Configure oscillators
    synth.set_oscillator("sine", True, 0.3)
    synth.set_oscillator("square", True, 0.1)
    synth.set_oscillator("triangle", False)
    synth.set_oscillator("sawtooth", False)
    
    # Set filter cutoff
    synth.set_filter(2000)
    
    # Play a few notes
    import time
    
    # C major scale frequencies
    frequencies = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
    
    for freq in frequencies:
        synth.play_note(freq, 0.5)
        time.sleep(0.6)
