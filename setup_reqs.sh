#!/bin/bash

sudo apt-get update
sudo apt-get install -y python3-dev python3-pip portaudio19-dev libportaudio2 libportaudiocpp0 libsndfile1-dev jackd2


# Check if JACK is installed correctly
if ! command -v jackd &> /dev/null; then
    echo "JACK installation failed. Trying again..."
    sudo apt-get install -y jackd2
fi

# Configure JACK to work without real-time privileges
# This creates a .jackdrc file in the home directory
echo "/usr/bin/jackd -dalsa -dhw:0 -r44100 -p1024 -n2" > ~/.jackdrc



