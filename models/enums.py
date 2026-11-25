from enum import Enum


class ActivityLevel(str, Enum):
    NOT_ACTIVE = "not_active"
    LITTLE_ACTIVITY = "little_activity"
    MODERATE = "moderate"
    ACTIVE = "active"
    VERY_ACTIVE = "very_active"


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class Period(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
