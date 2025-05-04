from pyo import *
from time import time


clap_path = "imogenviz/soundbank/clap-fat.wav"
hihat_path = "imogenviz/soundbank/hihat-808.wav"
kick_path = "imogenviz/soundbank/kick-electro01.wav"
snare_path = "imogenviz/soundbank/snare-analog.wav"

class Drums:
    def __init__(self, server=None):
        # Load drum samples into SndTable objects
        self.kick = SndTable(kick_path)
        self.snare = SndTable(snare_path)
        self.hihat = SndTable(hihat_path)
        self.clap = SndTable(clap_path)
        
        # Create TableRead objects to play the samples
        self.kick_player = TableRead(self.kick, freq=self.kick.getRate(), loop=False, mul=0.7)
        self.snare_player = TableRead(self.snare, freq=self.snare.getRate(), loop=False, mul=0.7)
        self.hihat_player = TableRead(self.hihat, freq=self.hihat.getRate(), loop=False, mul=0.7)
        self.clap_player = TableRead(self.clap, freq=self.clap.getRate(), loop=False, mul=0.7)
        
        # Connect to audio output
        self.kick_player.out()
        self.snare_player.out()
        self.hihat_player.out()
        self.clap_player.out()

    def play_kick(self):
        print("playing kick")
        self.kick_player.stop()
        self.kick_player.play()
    
    def play_snare(self):
        print("playing snare")
        self.snare_player.stop()
        self.snare_player.play()
    
    def play_hihat(self):
        print("playing hihat")
        self.hihat_player.stop()
        self.hihat_player.play()

    def play_clap(self):
        print("playing clap")
        self.clap_player.stop()
        self.clap_player.play()


