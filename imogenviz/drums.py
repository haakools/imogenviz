from pyo import *
from time import time


clap_path = "imogenviz/soundbank/clap-fat.wav"
hihat_path = "imogenviz/soundbank/hihat-808.wav"
kick_path = "imogenviz/soundbank/kick-electro01.wav"
snare_path = "imogenviz/soundbank/snare-analog.wav"

class Drums:
    def __init__(self, server=None):
        # Load samples into tables
        self.kick = SndTable(kick_path)
        self.snare = SndTable(snare_path)
        self.hihat = SndTable(hihat_path)
        self.clap = SndTable(clap_path)
        
        # Create metro objects (set to 0 so they don't trigger automatically)
        self.kick_metro = Metro(time=0)
        self.snare_metro = Metro(time=0)
        self.hihat_metro = Metro(time=0)
        self.clap_metro = Metro(time=0)
        
        # Create triggers that will play the sounds
        self.kick_trig = TrigEnv(self.kick_metro, table=self.kick, dur=self.kick.getDur(), mul=0.7)
        self.snare_trig = TrigEnv(self.snare_metro, table=self.snare, dur=self.snare.getDur(), mul=0.7)
        self.hihat_trig = TrigEnv(self.hihat_metro, table=self.hihat, dur=self.hihat.getDur(), mul=0.7)
        self.clap_trig = TrigEnv(self.clap_metro, table=self.clap, dur=self.clap.getDur(), mul=0.7)
        
        # Connect to output
        self.kick_trig.out()
        self.snare_trig.out()
        self.hihat_trig.out()
        self.clap_trig.out()
    
    def play_kick(self):
        print("playing kick")
        # Send a single trigger
        self.kick_metro.play(0)
    
    def play_snare(self):
        print("playing snare")
        self.snare_metro.play(0)
    
    def play_hihat(self):
        print("playing hihat")
        self.hihat_metro.play(0)
        
    def play_clap(self):
        print("playing clap")
        self.clap_metro.play(0)

