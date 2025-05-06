from pyo import *
import time
import os

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
        
        # Create trig objects for manual triggering
        self.kick_trig = Trig()
        self.snare_trig = Trig()
        self.hihat_trig = Trig()
        self.clap_trig = Trig()
        
        # Create players that will play the sounds when triggered
        self.kick_player = TrigEnv(self.kick_trig, table=self.kick, dur=self.kick.getDur(), mul=0.7)
        self.snare_player = TrigEnv(self.snare_trig, table=self.snare, dur=self.snare.getDur(), mul=0.7)
        self.hihat_player = TrigEnv(self.hihat_trig, table=self.hihat, dur=self.hihat.getDur(), mul=0.7)
        self.clap_player = TrigEnv(self.clap_trig, table=self.clap, dur=self.clap.getDur(), mul=0.7)
        
        # Connect to output
        self.kick_player.out()
        self.snare_player.out()
        self.hihat_player.out()
        self.clap_player.out()
    
    def play_kick(self):
        print("playing kick")
        # Send a single trigger
        self.kick_trig.play()
    
    def play_snare(self):
        print("playing snare")
        self.snare_trig.play()
    
    def play_hihat(self):
        print("playing hihat")
        self.hihat_trig.play()
        
    def play_clap(self):
        print("playing clap")
        self.clap_trig.play()

if __name__ == "__main__":
    from pyo_server import setup_server, close_server
    
    server = setup_server()
    drums = Drums(server)
    
    # Wait for server to initialize
    time.sleep(1)
    
    print("Testing drums...")
    drums.play_kick()
    time.sleep(1)
    drums.play_snare()
    time.sleep(1)
    drums.play_hihat()
    time.sleep(1)
    drums.play_clap()
    time.sleep(1)
    
    # Keep the server running for a few seconds to hear all sounds
    time.sleep(5)
    
    print("Closing server...")
    close_server(server)
