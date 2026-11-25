from dataclasses import asdict, dataclass

from models.enums import Period


@dataclass
class LogRequest:
    type: object
    minutes: object


@dataclass
class ActivityRequest:
    name: object
    calories_per_60_min: object


@dataclass
class PeriodRequest:
    period: object


@dataclass
class UserRequest:
    age: object
    gender: object
    weight_kg: object
    height_cm: object
    goal: object


@dataclass
class LogRow:
    type: object
    minutes: object
    logged_at: str


@dataclass
class ActivityRecord:
    name: str
    calories_per_60_min: object


@dataclass
class ActivityLogged:
    event: str
    type: str
    minutes: object
    calories: int
    at: str


@dataclass
class WeeklyGoalReached:
    event: str
    calories: int
    goal: int
    at: str


@dataclass
class UserRecord:
    age: object
    gender: object
    weight_kg: object
    height_cm: object
    goal: object


@dataclass
class LogResponse:
    type: str
    minutes: object
    calories: int
    logged_at: str
    weekly_calories: int
    weekly_goal: int
    goal_reached: bool


@dataclass
class ActivityResponse:
    name: str
    calories_per_60_min: object


@dataclass
class CaloriesLog:
    type: str
    minutes: object
    logged_at: str
    calories: int


@dataclass
class CaloriesResponse:
    period: Period
    window_from: str
    to: str
    total_calories: int
    count: int
    logs: list[CaloriesLog]

    def to_dict(self) -> dict:
        period = (
            self.period.value
            if isinstance(self.period, Period)
            else self.period
        )
        return {
            "period": period,
            "from": self.window_from,
            "to": self.to,
            "total_calories": self.total_calories,
            "count": self.count,
            "logs": [asdict(row) for row in self.logs],
        }


@dataclass
class UserProfileResponse:
    age: object
    gender: str
    weight_kg: object
    height_cm: object
    goal: str


@dataclass
class TargetsResponse:
    period: Period
    calories_burned: int
    weekly_calories: int
    activity_level: str
    activity: str
    daily_targets: object
    bmr: object
    tdee: object


@dataclass
class RequestStatsResponse:
    count: int
    last_path: str
    last_seconds: float


@dataclass
class ErrorResponse:
    error: str


@dataclass
class MacrosQuery:
    age: object
    gender: str
    weight_kg: object
    height_cm: object
    activity: str
    goal: str
