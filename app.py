import json
import urllib.parse
import urllib.request
from dataclasses import asdict
from datetime import datetime, timedelta

from flask import Flask, jsonify, request

from builders.calories_response import CaloriesResponseBuilder
from decorators.request_log import request_log
from factories.records import (
    burned_calories,
    create_activity_logged,
    create_activity_record,
    create_activity_records,
    create_activity_request,
    create_activity_response,
    create_calories_log,
    create_error,
    create_log_records,
    create_log_request,
    create_log_response,
    create_log_row,
    create_macros_query,
    create_notice_records,
    create_period_request,
    create_request_stats_response,
    create_targets_response,
    create_user_profile_response,
    create_user_records,
    create_user_request,
    create_weekly_goal_reached,
)
from models.const import ACTIVITY_FOR_API, CAL_PER_HOUR, LIFESTYLE_ACTIVITY
from models.enums import ActivityLevel, Gender, Period
from singletons.requests import RequestsSingleton

app = Flask(__name__)


def read_json(path, default):
    try:
        with open(path, "r") as source:
            return json.loads(source.read())
    except Exception as err:
        print("could not read", path, err)
        return default


def write_json(path, value):
    with open(path, "w") as destination:
        destination.write(json.dumps(value, indent=2))


def error(message, status=400):
    return jsonify(asdict(create_error(message))), status


@app.route("/log", methods=["POST"])
@request_log
def log_activity():
    return _log_activity()


def _log_activity():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return error("body must be a json object")

    incoming = create_log_request(body.get("type"), body.get("minutes"))
    if incoming.type is None or incoming.minutes is None:
        return error("type and minutes are required")

    try:
        minutes = float(incoming.minutes)
    except (TypeError, ValueError):
        return error("minutes must be a number")
    if minutes <= 0:
        return error("minutes must be greater than 0")
    if minutes == int(minutes):
        minutes = int(minutes)

    activity_records = create_activity_records(read_json("data/activities.json", []))
    found = next(
        (row for row in activity_records if row.name == incoming.type),
        None,
    )
    if found is None:
        return error("unknown activity")

    calories = burned_calories(found.calories_per_60_min, minutes)
    logged_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    entry = create_log_row(incoming.type, minutes, logged_at)

    log_records = create_log_records(read_json("data/logs.json", []))
    log_records.append(entry)
    write_json("data/logs.json", [asdict(row) for row in log_records])

    now = datetime.now()
    week_start = now - timedelta(days=7)
    week_total = 0
    for item in log_records:
        when = datetime.strptime(item.logged_at, "%Y-%m-%dT%H:%M:%S")
        if not (week_start <= when <= now):
            continue
        row = next(
            (activity for activity in activity_records if activity.name == item.type),
            None,
        )
        if row is not None:
            week_total += burned_calories(row.calories_per_60_min, item.minutes)

    notice_records = create_notice_records(read_json("data/notices.json", []))
    notice_records.append(
        create_activity_logged(
            {
                "event": "activity_logged",
                "type": entry.type,
                "minutes": entry.minutes,
                "calories": calories,
                "at": entry.logged_at,
            }
        )
    )
    if week_total >= 500:
        notice_records.append(create_weekly_goal_reached(week_total, entry.logged_at))

    write_json("data/notices.json", [asdict(row) for row in notice_records])
    response = create_log_response(
        entry,
        calories,
        week_total,
        500,
        week_total >= 500,
    )
    return jsonify(asdict(response)), 201


@app.route("/log/undo", methods=["POST"])
@request_log
def undo_log():
    log_records = create_log_records(read_json("data/logs.json", []))
    if not log_records:
        return error("nothing to undo")
    removed = log_records.pop()
    write_json("data/logs.json", [asdict(row) for row in log_records])
    return jsonify(asdict(removed)), 200


@app.route("/notices", methods=["GET"])
@request_log
def list_notices():
    notice_records = create_notice_records(read_json("data/notices.json", []))
    return jsonify([asdict(row) for row in notice_records])


@app.route("/stats", methods=["GET"])
@request_log
def stats():
    requests = RequestsSingleton.get_instance()
    response = create_request_stats_response(
        requests.count,
        requests.last_path,
        requests.last_seconds,
    )
    return jsonify(asdict(response))


@app.route("/activities", methods=["GET"])
@request_log
def list_activities():
    activity_records = create_activity_records(read_json("data/activities.json", []))
    return jsonify([asdict(row) for row in activity_records])


@app.route("/activities", methods=["POST"])
@request_log
def add_activity():
    return _add_activity()


def _add_activity():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return error("body must be a json object")

    incoming = create_activity_request(
        body.get("name"),
        body.get("calories_per_60_min"),
    )
    if incoming.name is None or incoming.calories_per_60_min is None:
        return error("name and calories_per_60_min are required")
    if not isinstance(incoming.name, str) or incoming.name.strip() == "":
        return error("name must be a non-empty string")
    incoming.name = incoming.name.strip()

    try:
        calories = float(incoming.calories_per_60_min)
    except (TypeError, ValueError):
        return error("calories_per_60_min must be a number")
    if calories <= 0:
        return error("calories_per_60_min must be greater than 0")
    if calories == int(calories):
        calories = int(calories)
    incoming.calories_per_60_min = calories

    activity_records = create_activity_records(read_json("data/activities.json", []))
    if any(row.name == incoming.name for row in activity_records):
        return error("activity already exists")

    activity_records.append(
        create_activity_record(incoming.name, incoming.calories_per_60_min)
    )
    write_json(
        "data/activities.json",
        [
            {
                "name": row.name,
                CAL_PER_HOUR: row.calories_per_60_min,
            }
            for row in activity_records
        ],
    )
    response = create_activity_response(incoming)
    return jsonify(asdict(response)), 201


@app.route("/calories", methods=["GET"])
@request_log
def calories():
    return _calories()


def _calories():
    incoming = create_period_request(request.args.get("period"))
    now = datetime.now()
    try:
        period = Period(incoming.period)
    except ValueError:
        return error("period must be day, week or month")

    if period == Period.DAY:
        start = now - timedelta(days=1)
    elif period == Period.WEEK:
        start = now - timedelta(days=7)
    else:
        start = now - timedelta(days=30)

    log_records = create_log_records(read_json("data/logs.json", []))
    activity_records = create_activity_records(read_json("data/activities.json", []))
    total = 0
    matched = []
    for item in log_records:
        when = datetime.strptime(item.logged_at, "%Y-%m-%dT%H:%M:%S")
        if not (start <= when <= now):
            continue
        row = next(
            (activity for activity in activity_records if activity.name == item.type),
            None,
        )
        if row is None:
            continue
        burned = burned_calories(row.calories_per_60_min, item.minutes)
        total += burned
        matched.append(create_calories_log(item, burned))

    builder = CaloriesResponseBuilder()
    builder.set_window(period, start, now)
    builder.add_totals(total, len(matched))
    builder.add_logs(matched)
    return jsonify(builder.get_result().to_dict())


@app.route("/user", methods=["POST"])
@request_log
def save_user():
    return _save_user()


def _save_user():
    incoming = create_user_request(
        request.args.get("age"),
        request.args.get("gender"),
        request.args.get("weight_kg"),
        request.args.get("height_cm"),
        request.args.get("goal"),
    )
    if any(
        value is None
        for value in (
            incoming.age,
            incoming.gender,
            incoming.weight_kg,
            incoming.height_cm,
            incoming.goal,
        )
    ):
        return error("age, gender, weight_kg, height_cm and goal are required")

    try:
        age = float(incoming.age)
        weight_kg = float(incoming.weight_kg)
        height_cm = float(incoming.height_cm)
    except (TypeError, ValueError):
        return error("age, weight_kg and height_cm must be numbers")
    if age <= 0 or weight_kg <= 0 or height_cm <= 0:
        return error("age, weight_kg and height_cm must be greater than 0")

    if age == int(age):
        age = int(age)
    if weight_kg == int(weight_kg):
        weight_kg = int(weight_kg)
    if height_cm == int(height_cm):
        height_cm = int(height_cm)

    gender_text = incoming.gender.strip().lower()
    try:
        gender = Gender(gender_text)
    except ValueError:
        return error("gender must be male or female")

    goal = incoming.goal.strip().lower()
    if goal not in ("lose", "maintain", "gain"):
        return error("goal must be lose, maintain or gain")

    incoming.age = age
    incoming.gender = gender.value
    incoming.weight_kg = weight_kg
    incoming.height_cm = height_cm
    incoming.goal = goal
    write_json("data/user.json", asdict(incoming))

    response = create_user_profile_response(incoming)
    return jsonify(asdict(response)), 200


@app.route("/targets", methods=["GET"])
@request_log
def daily_targets():
    return _daily_targets()


def _daily_targets():
    incoming = create_period_request(request.args.get("period"))
    now = datetime.now()
    try:
        period = Period(incoming.period)
    except ValueError:
        return error("period must be day, week or month")

    if period == Period.DAY:
        start = now - timedelta(days=1)
    elif period == Period.WEEK:
        start = now - timedelta(days=7)
    else:
        start = now - timedelta(days=30)

    user_data = read_json("data/user.json", None)
    if user_data is None:
        return error("user is not saved")
    required = ("age", "gender", "weight_kg", "height_cm", "goal")
    if any(key not in user_data for key in required):
        return error("saved user is missing details")
    try:
        gender = Gender(user_data["gender"])
    except ValueError:
        return error("saved user gender is not supported")

    user_records = create_user_records(user_data)
    saved_user = user_records[0]
    log_records = create_log_records(read_json("data/logs.json", []))
    activity_records = create_activity_records(read_json("data/activities.json", []))
    total = 0
    for item in log_records:
        when = datetime.strptime(item.logged_at, "%Y-%m-%dT%H:%M:%S")
        if not (start <= when <= now):
            continue
        row = next(
            (activity for activity in activity_records if activity.name == item.type),
            None,
        )
        if row is not None:
            total += burned_calories(row.calories_per_60_min, item.minutes)

    if period == Period.DAY:
        weekly_calories = total * 7
    elif period == Period.WEEK:
        weekly_calories = total
    else:
        weekly_calories = int(round(total * 7 / 30))

    level = ActivityLevel.NOT_ACTIVE
    for name in (
        ActivityLevel.NOT_ACTIVE,
        ActivityLevel.LITTLE_ACTIVITY,
        ActivityLevel.MODERATE,
        ActivityLevel.ACTIVE,
        ActivityLevel.VERY_ACTIVE,
    ):
        band = LIFESTYLE_ACTIVITY[name][gender]
        if weekly_calories >= band["min_calories_per_week"]:
            level = name

    api_activity = ACTIVITY_FOR_API[level]
    query = create_macros_query(
        saved_user.age,
        gender.value,
        saved_user.weight_kg,
        saved_user.height_cm,
        api_activity,
        saved_user.goal,
    )
    query_string = urllib.parse.urlencode(asdict(query))
    url = "https://calorieapiadmin.com/api/v1/public/calc/macros?" + query_string
    try:
        outgoing = urllib.request.Request(
            url,
            headers={"User-Agent": "calorie-lab/1.0"},
        )
        remote = urllib.request.urlopen(outgoing, timeout=10)
        payload = json.loads(remote.read().decode())
        remote.close()
    except Exception as err:
        print("macros api failed", err)
        return error("could not load daily targets"), 502

    activity_level = level.value.replace("_", " ")
    response = create_targets_response(
        period,
        total,
        weekly_calories,
        activity_level,
        api_activity,
        payload.get("daily_targets"),
        payload.get("bmr"),
        payload.get("tdee"),
    )
    return jsonify(asdict(response))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
