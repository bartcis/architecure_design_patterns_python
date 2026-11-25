from models.enums import ActivityLevel, Gender

CAL_PER_HOUR = "calories_per_60_min"
MIN_CAL_PER_WEEK = "min_calories_per_week"
MAX_CAL_PER_WEEK = "max_calories_per_week"

LIFESTYLE_ACTIVITY = {
    ActivityLevel.NOT_ACTIVE: {
        Gender.MALE: {"min_calories_per_week": 13461, "max_calories_per_week": 18151},
        Gender.FEMALE: {"min_calories_per_week": 10955, "max_calories_per_week": 14105},
    },
    ActivityLevel.LITTLE_ACTIVITY: {
        Gender.MALE: {"min_calories_per_week": 14791, "max_calories_per_week": 19572},
        Gender.FEMALE: {"min_calories_per_week": 12019, "max_calories_per_week": 15218},
    },
    ActivityLevel.MODERATE: {
        Gender.MALE: {"min_calories_per_week": 15400, "max_calories_per_week": 19600},
        Gender.FEMALE: {"min_calories_per_week": 12600, "max_calories_per_week": 15400},
    },
    ActivityLevel.ACTIVE: {
        Gender.MALE: {"min_calories_per_week": 16079, "max_calories_per_week": 20804},
        Gender.FEMALE: {"min_calories_per_week": 12978, "max_calories_per_week": 16170},
    },
    ActivityLevel.VERY_ACTIVE: {
        Gender.MALE: {"min_calories_per_week": 17745, "max_calories_per_week": 22883},
        Gender.FEMALE: {"min_calories_per_week": 14455, "max_calories_per_week": 17752},
    },
}

ACTIVITY_FOR_API = {
    ActivityLevel.NOT_ACTIVE: "sedentary",
    ActivityLevel.LITTLE_ACTIVITY: "lightly_active",
    ActivityLevel.MODERATE: "moderately_active",
    ActivityLevel.ACTIVE: "very_active",
    ActivityLevel.VERY_ACTIVE: "extra_active",
}
