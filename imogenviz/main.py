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



chord_progression = [
    ("C", "major", 4),
    ("F", "sus4", 4),
    ("F", "maj7", 4),
    ("G", "dom7", 4),
    ("A", "minor", 4)
]

def main():

    ctime = 0
    ptime = 0
    cap = cv2.VideoCapture(0)
    detector = HandTrackingDynamic()
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    server = setup_server()
    pad = PAD(server=server)
    drums = Drums(server=server)
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    print("Press 'q' to quit")

    pad.play_chord("F", "maj7", 4)
    # Chord and cooldown values
    current_chord: Tuple = ("F", "maj7", 4)
    current_index = 0
    last_played_time = 0
    kick_last_played = 0
    timeout = 0.200 # seconds
    ptime = 0
   
    # finger values
    thumb = LimbPosition()
    index_finger = LimbPosition()
    index_finger_pip = LimbPosition()
    thumb_index_distance: float = 0.0
    resonance: float = 0.0

    while True:
        ret, frame = cap.read()
        frame = detector.findFingers(frame) 

        limb_list_one, bbox_left = detector.findPosition(frame, handNo=0)
        try:  
            limb_list_two, bbox_right = detector.findPosition(frame, handNo=1)
        except Exception as e:
            print("ERROR: ", e)
            limb_list_two = []

        # default guess, left limb always defined
        left_limb_list = limb_list_one
        right_limb_list = limb_list_two

        # assigning left hand to left part of screen, right to right
        if len(limb_list_two) > 0:
            if limb_list_one[0].x > limb_list_two[0].x:
                left_limb_list = limb_list_two
                right_limb_list = limb_list_one

        for limb in left_limb_list:
            if limb.index == LimbIndex.THUMB_TIP:
                thumb = limb
                print(thumb)
            if limb.index == LimbIndex.INDEX_FINGER_TIP:
                index_finger = limb
                print(index_finger)
            if limb.index == LimbIndex.INDEX_FINGER_PIP:
                index_finger_pip = limb
                print(index_finger_pip)
       
        if (index_finger_pip.y < index_finger.y) and ( ctime - kick_last_played) >= timeout:
            drums.play_kick()
            kick_last_played = ctime

        # goes from 15 to 200 -> map so its a logarithmic scale from 10 to 20000
        thumb_index_distance = r2distance(thumb, index_finger)
        print(f"thumb_index_distance: {thumb_index_distance}")
        thumb_index_distance = max(15, min(200, thumb_index_distance))
        cutoff_freq = float(20000 - (np.log(thumb_index_distance/15)/np.log(200/15)) * 19990)

        # normalized between 55-110 and poor mans clamp
        distance_hands = max(0, (average_distance(right_limb_list)-20)/(150-20))
    

        # todo: get multiprocessing for this
        if distance_hands > 0.8 and ( ctime - last_played_time) >= timeout:
            chord = chord_progression[current_index]
            current_chord = chord
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
