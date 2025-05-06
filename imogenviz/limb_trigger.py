# multiprocessing class to handle calculations of
# trigger events

import threading
import time
from dataclasses import dataclass

from limbs import (
        LimbIndex,
        LimbPosition,
        r2distance,
        average_distance,
        calculate_center_of_mass
        )


@dataclass
class GestureData:
    # Calculated metrics
    thumb_index_distance: float = 0.0
    index_finger_bent: bool = False
    middle_finger_bent: bool = False
    ring_finger_bent: bool = False
    hand_size: float = 0.0
    average_position: float = 0.0


def process_hand(limb_list: list[LimbPosition]):
    # TODO swaft the limb_list with something indexable as there are many
    # different values
    thumb = None
    index_finger_pip = None
    index_finger_tip = None
    middle_finger_pip = None
    middle_finger_tip = None
    ring_finger_pip = None
    ring_finger_tip = None

    for limb in limb_list:
        if limb.index == LimbIndex.THUMB_TIP:
            thumb = limb
        if limb.index == LimbIndex.INDEX_FINGER_PIP:
            index_finger_pip = limb
        if limb.index == LimbIndex.INDEX_FINGER_TIP:
            index_finger_tip = limb
            
        if limb.index == LimbIndex.MIDDLE_FINGER_PIP:
            middle_finger_pip = limb
        if limb.index == LimbIndex.MIDDLE_FINGER_TIP:
            middle_finger_tip = limb

        if limb.index == LimbIndex.RING_FINGER_PIP:
            ring_finger_pip = limb
        if limb.index == LimbIndex.RING_FINGER_TIP:
            ring_finger_tip = limb

    # normalized between 150 and 0 
    distance_hands = max(0, (average_distance(limb_list)-20)/(150-20))

    return GestureData(
            thumb_index_distance = r2distance(thumb, index_finger_tip),
            index_finger_bent = check_finger_bent(index_finger_pip, index_finger_tip),
            middle_finger_bent = check_finger_bent(middle_finger_pip, middle_finger_tip),
            ring_finger_bent = check_finger_bent(ring_finger_pip, ring_finger_tip),
            hand_size = distance_hands
        )

def check_finger_bent(pip, tip):
    if pip is None or tip is None:
        return False
    if pip.y < tip.y:
        return True
    return False

