

from dataclasses import dataclass

from enum import Enum
import math as math


class LimbIndex(Enum):
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_FINGER_MCP = 5
    INDEX_FINGER_PIP = 6
    INDEX_FINGER_DIP = 7
    INDEX_FINGER_TIP = 8
    MIDDLE_FINGER_MCP = 9
    MIDDLE_FINGER_PIP = 10
    MIDDLE_FINGER_DIP = 11
    MIDDLE_FINGER_TIP = 12
    RING_FINGER_MCP = 13
    RING_FINGER_PIP = 14
    RING_FINGER_DIP = 15
    RING_FINGER_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20

@dataclass
class LimbPosition:
    index: LimbIndex
    x: int = 0
    y: int = 0

    def __str__(self):
        return f"{self.index.name} - (x,y) = {(self.x), (self.y)}"

    def __repr__(self):
        return self.__str__()

    def xypos(self) -> tuple[int,int]:
        return self.x, self.y

def r2distance(pos1: LimbPosition, pos2: LimbPosition) -> float:
    """Calculate Euclidean distance between two LimbPosition objects"""
    if (pos1 is None) or (pos2 is None):
        return 0.0
    
    if pos1.x is None or pos1.y is None or pos2.x is None or pos2.y is None:
        raise ValueError("Cannot calculate distance with None coordinates")
        
    return math.sqrt((pos2.x - pos1.x) ** 2 + (pos2.y - pos1.y) ** 2)

def average_distance(positions: list[LimbPosition]) -> float:
    """Calculate average pairwise distance between all LimbPosition objects"""
    if positions is None:
        return 0.0
    
    if len(positions) == 0:
        return 0.0
    
    if len(positions) < 2:
        raise ValueError("Need at least 2 positions to calculate average distance")
        
    total_distance = 0
    num_pairs = 0
    
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            total_distance += r2distance(positions[i], positions[j])
            num_pairs += 1
            
    return total_distance / num_pairs

