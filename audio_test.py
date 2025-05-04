from pyo import *
import time
import os
import subprocess

# Suppress ALSA error messages
os.environ['ALSA_OUTPUT_STDERR'] = '0'

# Function to get default PulseAudio sink index
def get_default_pulse_sink():
    try:
        # Get the name of the default sink
        result = subprocess.run(['pactl', 'info'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'Default Sink:' in line:
                default_sink_name = line.split('Default Sink: ')[1].strip()
                
                # Get the index of this sink
                sinks = subprocess.run(['pactl', 'list', 'short', 'sinks'], capture_output=True, text=True)
                for sink_line in sinks.stdout.split('\n'):
                    if sink_line and default_sink_name in sink_line:
                        return int(sink_line.split('\t')[0])
        return 0  # Default to 0 if we can't determine
    except Exception as e:
        print(f"Error getting default sink: {e}")
        return 0

# Function to check if JACK is running
def is_jack_running():
    try:
        result = subprocess.run(['jack_control', 'status'], capture_output=True, text=True)
        return "started" in result.stdout.lower()
    except:
        return False

# Function to list available pyo audio backends
def list_available_backends():
    print("\nAvailable pyo audio backends:")
    for backend in ['jack', 'portaudio', 'pa', 'coreaudio', 'offline']:
        try:
            # Create a test server to see if the backend is available
            test_server = Server(audio=backend)
            print(f"- {backend} (available)")
        except:
            print(f"- {backend} (not available)")

# Determine the best audio backend to use
print("Checking audio system...")
if is_jack_running():
    print("JACK audio server detected!")
    audio_backend = 'jack'
    print("Using JACK audio - this should work well with other audio applications")
else:
    print("JACK not running, using PortAudio with PulseAudio")
    audio_backend = 'pa'  # PortAudio will use PulseAudio on Linux

# List backends and available devices
list_available_backends()

# Display audio devices
print("\nAvailable audio devices:")
pa_list_devices()

# Try to get the default PulseAudio sink
default_device = get_default_pulse_sink()
print(f"\nDetected default PulseAudio sink: {default_device}")

# Let user choose the device
device_input = input(f"Enter output device number (press Enter for default {default_device}): ")
if device_input.strip():
    OUTPUT_DEVICE = int(device_input)
else:
    OUTPUT_DEVICE = default_device

# Audio configuration
SAMPLING_RATE = 44100  # Standard rate
N_CHANNELS = 2
BUFFERSIZE = 1024  # Larger buffer for better stability

# Server configuration for better compatibility
s = Server(
    sr=SAMPLING_RATE,
    nchnls=N_CHANNELS,
    buffersize=BUFFERSIZE,
    duplex=0,  # Output only for now
    audio=audio_backend,
    jackname="pyo_test"
)

# Set output device (not needed if using JACK)
if audio_backend != 'jack':
    s.setOutputDevice(OUTPUT_DEVICE)

try:
    print(f"Starting audio server with {audio_backend} backend on device {OUTPUT_DEVICE}...")
    s.boot()
    
    # Wait a moment before starting the server
    time.sleep(0.5)
    s.start()
    print("Server started successfully!")
    
    # Create a simple sine wave
    sine = Sine(freq=440, mul=0.3)
    
    # Add a fade-in to avoid clicks
    fade = Fader(fadein=0.1, fadeout=0.1, dur=0).play()
    output = sine * fade
    
    # Output to both channels
    stereo = Mix(output, voices=2).out()
    
    print("\nPlaying a 440 Hz sine wave for 5 seconds...")
    print("You should be able to record this with screen recorder now")
    print("If not, check your screen recorder's audio input settings")
    
    # Keep the script running for 5 seconds
    time.sleep(5)
    
    # Graceful shutdown with fade out
    fade.stop()
    time.sleep(0.2)  # Short delay to allow fade out
    
    # Clean up
    sine.stop()
    s.stop()
    s.shutdown()
    print("Audio test completed!")
    
except Exception as e:
    print(f"Error: {e}")
    print("\nTroubleshooting tips for Pop!_OS:")
    print("1. Install JACK: sudo apt install jackd2 qjackctl")
    print("2. Start JACK with QjackCtl and try again with 'jack' backend")
    print("3. Check if PulseAudio is running: pulseaudio --check")
    print("4. Try restarting PulseAudio: pulseaudio -k && pulseaudio --start")
    print("5. Make sure your user is in the 'audio' group: sudo usermod -a -G audio $USER")
