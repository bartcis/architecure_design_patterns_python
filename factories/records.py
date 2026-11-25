from models.const import CAL_PER_HOUR
from models.data import (
    ActivityLogged,
    ActivityRecord,
    ActivityRequest,
    ActivityResponse,
    CaloriesLog,
    ErrorResponse,
    LogRequest,
    LogResponse,
    LogRow,
    MacrosQuery,
    PeriodRequest,
    RequestStatsResponse,
    TargetsResponse,
    UserProfileResponse,
    UserRecord,
    UserRequest,
    WeeklyGoalReached,
)


def create_log_request(type, minutes):
    return LogRequest(type=type, minutes=minutes)


def create_activity_request(name, calories_per_60_min):
    return ActivityRequest(name=name, calories_per_60_min=calories_per_60_min)


def create_period_request(period):
    return PeriodRequest(period=period)


def create_user_request(age, gender, weight_kg, height_cm, goal):
    return UserRequest(
        age=age,
        gender=gender,
        weight_kg=weight_kg,
        height_cm=height_cm,
        goal=goal,
    )


def create_log_row(activity_type, minutes, logged_at):
    return LogRow(type=activity_type, minutes=minutes, logged_at=logged_at)


def create_log_records(rows):
    return [
        create_log_row(row["type"], row["minutes"], row["logged_at"]) for row in rows
    ]


def create_activity_record(name, calories_per_60_min):
    return ActivityRecord(name=name, calories_per_60_min=calories_per_60_min)


def create_activity_records(rows):
    return [create_activity_record(row["name"], row[CAL_PER_HOUR]) for row in rows]


def create_notice_records(rows):
    notices = []
    for row in rows:
        if row["event"] == "activity_logged":
            notices.append(create_activity_logged(row))
        elif row["event"] == "weekly_goal_reached":
            notices.append(
                WeeklyGoalReached(
                    event=row["event"],
                    calories=row["calories"],
                    goal=row["goal"],
                    at=row["at"],
                )
            )
    return notices


def create_user_records(row):
    return [
        UserRecord(
            age=row["age"],
            gender=row["gender"],
            weight_kg=row["weight_kg"],
            height_cm=row["height_cm"],
            goal=row["goal"],
        )
    ]


def create_activity_logged(row):
    if "event" in row:
        return ActivityLogged(
            event=row["event"],
            type=row["type"],
            minutes=row["minutes"],
            calories=row["calories"],
            at=row["at"],
        )
    return ActivityLogged(
        event="activity_logged",
        type=row["type"],
        minutes=row["minutes"],
        calories=row["calories"],
        at=row["logged_at"],
    )


def create_weekly_goal_reached(calories, at):
    return WeeklyGoalReached(
        event="weekly_goal_reached",
        calories=calories,
        goal=500,
        at=at,
    )


def create_log_response(
    entry,
    calories,
    weekly_calories,
    weekly_goal,
    goal_reached,
):
    return LogResponse(
        type=entry.type,
        minutes=entry.minutes,
        calories=calories,
        logged_at=entry.logged_at,
        weekly_calories=weekly_calories,
        weekly_goal=weekly_goal,
        goal_reached=goal_reached,
    )


def create_activity_response(activity):
    return ActivityResponse(
        name=activity.name,
        calories_per_60_min=activity.calories_per_60_min,
    )


def create_calories_log(row, calories):
    return CaloriesLog(
        type=row.type,
        minutes=row.minutes,
        logged_at=row.logged_at,
        calories=calories,
    )


def create_user_profile_response(user):
    return UserProfileResponse(
        age=user.age,
        gender=user.gender,
        weight_kg=user.weight_kg,
        height_cm=user.height_cm,
        goal=user.goal,
    )


def create_targets_response(
    period,
    calories_burned,
    weekly_calories,
    activity_level,
    activity,
    daily_targets,
    bmr,
    tdee,
):
    return TargetsResponse(
        period=period,
        calories_burned=calories_burned,
        weekly_calories=weekly_calories,
        activity_level=activity_level,
        activity=activity,
        daily_targets=daily_targets,
        bmr=bmr,
        tdee=tdee,
    )


def create_request_stats_response(count, last_path, last_seconds):
    return RequestStatsResponse(
        count=count,
        last_path=last_path,
        last_seconds=last_seconds,
    )


def create_error(message):
    return ErrorResponse(error=message)


def create_macros_query(
    age,
    gender,
    weight_kg,
    height_cm,
    activity,
    goal,
):
    return MacrosQuery(
        age=age,
        gender=gender,
        weight_kg=weight_kg,
        height_cm=height_cm,
        activity=activity,
        goal=goal,
    )


def burned_calories(calories_per_60_min, minutes):
    return int(round(calories_per_60_min * minutes / 60))
