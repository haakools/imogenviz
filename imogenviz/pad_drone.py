import numpy as np
import os
from pyo import *
import time

# Suppress ALSA error messages
os.environ['ALSA_OUTPUT_STDERR'] = '0'

# Global audio configuration (same as before)
SAMPLING_RATE = 48000
OUTPUT_DEVICE = 7
N_CHANNELS = 2
BUFFERSIZE = 512
DUPLEX = 0

pa_list_devices()




class PAD:
    def __init__(self, server=None):
        # Use existing server or create a new one
        if server is None:
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
            self.owns_server = True
        else:
            self.server = server
            self.owns_server = False
        
        # Define note frequency ratios for standard tuning
        self.note_ratios = {
            "C": 1.0,
            "C#": 1.059463,
            "D": 1.122462,
            "D#": 1.189207,
            "E": 1.259921,
            "F": 1.334840,
            "F#": 1.414214,
            "G": 1.498307,
            "G#": 1.587401,
            "A": 1.681793,
            "A#": 1.781797,
            "B": 1.887749
        }
        
        # Define chord structures (semitone intervals from root)
        self.chord_types = {
            "major": [0, 4, 7],  # Root, major third, perfect fifth
            "minor": [0, 3, 7],  # Root, minor third, perfect fifth
            "dim": [0, 3, 6],    # Root, minor third, diminished fifth
            "aug": [0, 4, 8],    # Root, major third, augmented fifth
            "sus4": [0, 5, 7],   # Root, perfect fourth, perfect fifth
            "maj7": [0, 4, 7, 11],  # Major with major seventh
            "min7": [0, 3, 7, 10],  # Minor with minor seventh
            "dom7": [0, 4, 7, 10]   # Major with minor seventh (dominant)
        }
        
        # Create oscillator banks for pad sounds (3 oscillators per voice x 4 voices)
        self.oscillators = []
        self.current_chord = None
        
        # Store the base oscillators that we'll use for each voice
        for i in range(12):  # Support for up to 12 notes (4 voices with 3 oscillators each)
            # Create slightly detuned oscillators for rich sound
            detune = random.uniform(-0.1, 0.1)  # Slight random detune for richness
            
            # Use different waveforms for each oscillator to create a rich pad sound
            if i % 3 == 0:
                # Sine wave for fundamental
                osc = Sine(freq=440 + detune, mul=0.0)
            elif i % 3 == 1:
                # Triangle for some harmonics
                osc = LFO(freq=440 + detune, type=2, mul=0.0)
            else:
                # Soft saw for more harmonics
                osc = Phasor(freq=440 + detune, mul=0.0)
            
            self.oscillators.append(osc)
        
        # Create mixer for all oscillators
        self.mixer = Mix(self.oscillators, voices=2)
        
        # Create filters with initial settings
        self.filter = MoogLP(self.mixer, freq=1000, res=0.5)
        
        # Add reverb for spaciousness
        self.reverb = Freeverb(self.filter, size=0.85, damp=0.5, bal=0.3)
        
        # Final output
        self.output = self.reverb.out()
        
        # Stop all oscillators initially
        for osc in self.oscillators:
            osc.stop()
    
    def play_chord(self, root_note, chord_type="major", base_octave=4):
        """
        Play a chord with the specified root note and type
        
        Parameters:
        - root_note: The root note of the chord (e.g., "C", "F#")
        - chord_type: The type of chord ("major", "minor", etc.)
        - base_octave: The octave of the root note (4 = middle C)
        """
        # Stop any currently playing chord
        self.stop_chord()
        
        # Save current chord info
        self.current_chord = {
            "root": root_note,
            "type": chord_type,
            "octave": base_octave
        }
        
        # Calculate base frequency for the root note
        base_freq = 261.63 * (2 ** (base_octave - 4))  # C4 = 261.63 Hz
        root_freq = base_freq * self.note_ratios[root_note]
        
        # Get the intervals for this chord type
        if chord_type in self.chord_types:
            intervals = self.chord_types[chord_type]
        else:
            print(f"Unknown chord type: {chord_type}, using major")
            intervals = self.chord_types["major"]
        
        # Calculate frequencies for each note in the chord
        note_freqs = []
        for interval in intervals:
            # Convert semitones to frequency ratio
            ratio = 2 ** (interval / 12)
            note_freqs.append(root_freq * ratio)
        
        # Add octaves for richness (standard technique for pads)
        extended_freqs = note_freqs.copy()
        for freq in note_freqs:
            # Add an octave up
            extended_freqs.append(freq * 2)
        
        # Assign frequencies to oscillators
        for i, osc in enumerate(self.oscillators):
            if i < len(extended_freqs):
                # Set frequency
                osc.freq = extended_freqs[i]
                
                # Set amplitude based on voice position (lower = louder)
                if i < len(note_freqs):
                    # Base notes are louder
                    amplitude = 0.2
                else:
                    # Higher octaves are quieter
                    amplitude = 0.1
                
                # Apply slight variation for each oscillator type
                if i % 3 == 0:
                    osc.mul = amplitude
                elif i % 3 == 1:
                    osc.mul = amplitude * 0.7
                else:
                    osc.mul = amplitude * 0.5
                
                # Start the oscillator
                osc.play()
        
        # Return the chord info
        return self.current_chord
    
    def stop_chord(self):
        """Stop all currently playing oscillators"""
        for osc in self.oscillators:
            osc.stop()
        self.current_chord = None
    
    def set_filter(self, cutoff_freq, resonance=0.5):
        """
        Set the filter cutoff frequency and resonance
        
        Parameters:
        - cutoff_freq: Cutoff frequency in Hz (20-20000)
        - resonance: Resonance amount (0.0-1.0)
        """
        # Ensure cutoff is in valid range
        cutoff_freq = max(20, min(20000, cutoff_freq))
        resonance = max(0.0, min(1.0, resonance))
        
        # Apply to filter
        self.filter.freq = cutoff_freq
        self.filter.res = resonance
        
        return {"cutoff": cutoff_freq, "resonance": resonance}
    
    def set_reverb(self, size=0.85, damp=0.5, balance=0.3):
        """
        Adjust reverb parameters for the pad sound
        
        Parameters:
        - size: Room size (0.0-1.0)
        - damp: Damping factor (0.0-1.0)
        - balance: Dry/wet balance (0.0-1.0)
        """
        self.reverb.size = size
        self.reverb.damp = damp
        self.reverb.bal = balance
    
    def close(self):
        """Clean up resources"""
        self.stop_chord()
        if self.owns_server:
            self.server.stop()
            self.server.shutdown()


# Example usage:
if __name__ == "__main__":
    # List available devices
    pa_list_devices()
    
    # Create a pad synth
    pad = PAD()
    
    # Play some chords with filter sweeps
    print("Playing C major chord...")
    pad.play_chord("C", "major", 4)
    
    # Slowly sweep the filter from low to high
    for i in range(50):
        # Exponential sweep from 300 to 5000 Hz
        cutoff = 300 * (5000/300) ** (i/49)
        pad.set_filter(cutoff, resonance=0.3)
        time.sleep(0.1)
    
    time.sleep(1)
    
    print("Playing A minor chord...")
    pad.play_chord("A", "minor", 3)
    
    # Sweep filter from high to low
    for i in range(50):
        # Exponential sweep from 5000 to 300 Hz
        cutoff = 5000 * (300/5000) ** (i/49)
        pad.set_filter(cutoff, resonance=0.7)
        time.sleep(0.1)
    
    time.sleep(1)
    
    print("Playing F major 7th chord...")
    pad.play_chord("F", "maj7", 4)
    
    # LFO-like filter sweep
    for i in range(100):
        # Sine wave motion for filter
        cutoff = 1000 + 2000 * np.sin(i * 0.1)
        pad.set_filter(cutoff, resonance=0.4)
        time.sleep(0.05)
    
    # Clean up
    pad.close()
    print("Done.")
