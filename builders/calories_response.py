from models.data import CaloriesResponse


class CaloriesResponseBuilder:
    def __init__(self):
        self.period = None
        self.window_from = None
        self.window_to = None
        self.total_calories = 0
        self.count = 0
        self.logs = []

    def set_window(self, period, start, end):
        self.period = period
        self.window_from = start.strftime("%Y-%m-%dT%H:%M:%S")
        self.window_to = end.strftime("%Y-%m-%dT%H:%M:%S")
        return self

    def add_totals(self, total, count):
        self.total_calories = total
        self.count = count
        return self

    def add_logs(self, matched):
        self.logs = matched
        return self

    def get_result(self):
        return CaloriesResponse(
            period=self.period,
            window_from=self.window_from,
            to=self.window_to,
            total_calories=self.total_calories,
            count=self.count,
            logs=self.logs,
        )
