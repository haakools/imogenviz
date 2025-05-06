import cv2
import numpy as np
import time
import math as math
from handtracking import HandTrackingDynamic
from pyo_server import setup_server, close_server
from limbs import (
        LimbIndex,
        LimbPosition,
        r2distance,
        average_distance,
        calculate_center_of_mass
        )
from drums import Drums
from pad_drone import PAD 
from limb_trigger import (
        GestureData,
        process_hand,
    )

chord_progression = [
    ("C", "major", 4),
    ("F", "sus4", 4),
    ("F", "maj7", 4),
    ("G", "dom7", 4),
    ("A", "minor", 4)
]

def main():
    
    # Setup camera
    ctime = 0
    ptime = 0
    cap = cv2.VideoCapture(0)
    detector = HandTrackingDynamic()
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
   
    # Setup instruments
    server = setup_server()
    pad = PAD(server=server)
    drums = Drums(server=server)
   
    # define trigger classes


    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    print("Press 'q' to quit")
    # Chord and cooldown values
    current_chord: Tuple = ("F", "maj7", 4)
    current_index = 0

    # event based cooldown values
    last_chord_change_time = 0

    last_kick_time = 0
    last_clap_time = 0
    last_hihat_time = 0
    last_snare_time = 0

    d_timeout = 0.8 # seconds, drums
    p_timeout = 2 # seconds, pad
    pad.play_chord(*current_chord)
   
    while True:
        ret, frame = cap.read()
        frame = detector.findFingers(frame) 

        # Below does not belong in main thread
        limb_list_one, bbox_left = detector.findPosition(frame, handNo=0)
        try:  
            limb_list_two, bbox_right = detector.findPosition(frame, handNo=1)
        except Exception as e:
            print("ERROR: ", e)
            limb_list_two = []

        left_limb_list = limb_list_one
        right_limb_list = limb_list_two
        # assigning left hand to left part of screen, right to right
        if len(limb_list_two) > 0:
            if limb_list_one[0].x > limb_list_two[0].x:
                left_limb_list = limb_list_two
                right_limb_list = limb_list_one

        left_hand: GestureData = process_hand(left_limb_list)
        right_hand: GestureData = process_hand(right_limb_list)

        # TODO MAP TO TRIGGER THREAD
        # LEFT HAND PROCESSING -> 
        if left_hand.index_finger_bent and ( ctime - last_kick_time) >= d_timeout:
            drums.play_kick()
            last_kick_time = ctime

        if left_hand.ring_finger_bent and ( ctime - last_snare_time) >= d_timeout:
            drums.play_snare()
            last_snare_time = ctime
       
        if left_hand.middle_finger_bent and ( ctime - last_hihat_time) >= d_timeout:
            drums.play_hihat()
            last_hihat_time = ctime

        # RIGHT HAND PROCESSING

        # goes from 15 to 200 -> map so its a logarithmic scale from 10 to 20000
        cutoff_freq = float(20000 - (np.log(right_hand.thumb_index_distance/15)/np.log(200/15)) * 19990)

        if right_hand.hand_size > 0.8 and ( ctime - last_chord_change_time) >= p_timeout:
            chord = chord_progression[current_index]
            current_chord = chord
            pad.play_chord(*chord)
        
            # Update tracking variables
            last_chord_change_time = ctime
            current_index = (current_index + 1) % len(chord_progression)

        pad.set_filter(cutoff_freq)

        if not ret:
            print("Error: Can't receive frame. Exiting...")
            break

        ctime = time.time()
        fps =1/(ctime-ptime)
        ptime = ctime

        cv2.putText(frame, str(int(fps)), (10,70), cv2.FONT_HERSHEY_PLAIN,3,(255,0,255),3)
        cv2.putText(
                frame, 
                str(current_chord[0]) + str(current_chord[1]) + " - octave:" + str(current_chord[2]),
                (10,140), cv2.FONT_HERSHEY_PLAIN,3,(255,0,255),3)

        cv2.imshow('Camera :)', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
