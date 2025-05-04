import cv2
import numpy as np
import time
import math as math
from handtracking import HandTrackingDynamic
from limbs import (
        LimbIndex,
        LimbPosition,
        r2distance,
        average_distance
        )

from pad_drone import PAD 



chord_progression = [
    ("C", "major", 4),
    ("F", "maj7", 4),
    ("G", "dom7", 4),
    ("A", "minor", 4)
]

# Function to process signal and play next chord
def process_chord_signal(pad, signal_value, current_index, last_played_time, timeout=2.0, threshold=0.5):
    current_time = time.time()
    
    if signal_value > threshold and (current_time - last_played_time) >= timeout:
        # Play the next chord
        chord = chord_progression[current_index]
        pad.play_chord(*chord)
        
        # Update tracking variables
        last_played_time = current_time
        current_index = (current_index + 1) % len(chord_progression)
        return current_index, last_played_time, True
    
    return current_index, last_played_time, False



def main():

    ctime = 0
    ptime = 0
    cap = cv2.VideoCapture(0)
    detector = HandTrackingDynamic()
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    pad = PAD(server=None) # start server
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    print("Press 'q' to quit")

    # make this play only on signal that it should play / change

    pad.play_chord("F", "maj7", 4)
    current_index = 0
    last_played_time = 0
    timeout = 2.0


    thumb = None
    index_finger = None
    thumb_index_distance: float = 0.0
    resonance: float = 0.0
    ptime = 0

    while True:
        ret, frame = cap.read()
        frame = detector.findFingers(frame) 
        left_limb_list, bbox_left = detector.findPosition(frame, handNo=0)
        #print("Length of left limb list:", len(left_limb_list)) 
        #print(left_limb_list)
        #print(25*"-")
        try:  
            right_limb_list, bbox_right = detector.findPosition(frame, handNo=1)
            #print("Length of right limb list:", len(right_limb_list)) 
            #print(right_limb_list)
            #print(25*"-")
        except Exception as e:
            print("ERROR: ", e)
            right_limb_list = []

        for limb in left_limb_list:
            print(limb)
            if limb.index == LimbIndex.THUMB_TIP:
                thumb = limb
                print(thumb)
            if limb.index == LimbIndex.INDEX_FINGER_TIP:
                index_finger = limb
                print(index_finger)
        # goes from 15 to 200 -> map so its a logarithmic scale from 10 to 20000
        thumb_index_distance = r2distance(thumb, index_finger)
        print(f"thumb_index_distance: {thumb_index_distance}")
        thumb_index_distance = max(15, min(200, thumb_index_distance))
        cutoff_freq = float(20000 - (np.log(thumb_index_distance/15)/np.log(200/15)) * 19990)

        # normalized between 55-110 and poor mans clamp
        distance_hands = max(0, (average_distance(right_limb_list)-20)/(150-20))

        if distance_hands > 0.8 and ( ctime - last_played_time) >= timeout:
            chord = chord_progression[current_index]
            pad.play_chord(*chord)
        
            # Update tracking variables
            last_played_time = ctime
            current_index = (current_index + 1) % len(chord_progression)
        
            print(f"Playing chord: {chord}")

        pad.set_filter(cutoff_freq)

        if not ret:
            print("Error: Can't receive frame. Exiting...")
            break
        ctime = time.time()
        fps =1/(ctime-ptime)
        ptime = ctime

        cv2.putText(frame, str(int(fps)), (10,70), cv2.FONT_HERSHEY_PLAIN,3,(255,0,255),3)

        cv2.imshow('Camera :)', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
