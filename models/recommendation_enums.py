from enum import Enum


class Sex(Enum):
    MALE = 1
    FEMALE = 2


class ActivityFactor(Enum):
    SEDENTARY = 1.2
    LIGHT = 1.375
    MEDIUM = 1.55
    HARD = 1.725


class AgeFactor(Enum):
    MALE = 5
    FEMALE = -161