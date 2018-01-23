from collections import defaultdict, Counter
from itertools import groupby
from time import mktime

from dateutil.relativedelta import relativedelta


class CalendarHeatMap:
    """requires: d3 3.5.6"""

    html = """
    <div class={class_name}></div>
    <script type="text/javascript">
        var cal = new CalHeatMap();
        cal.init({{data: {data},
                  itemSelector: ".{class_name}",
                  domain:"{domain}",
                  start:{start},
                  itemName: ["% winrate", "% winrate"],
                  tooltip: true,
                  range: {range},
                  legend: [20, 40, 60, 80],
        }});
    </script>
    """

    def __init__(self, matches):
        by_day = groupby(matches, lambda m: m.time.date())
        self.data = {
            mktime(day.timetuple()): self._get_winrate(matches)
            for day, matches in by_day
            if matches
        }
        self.start = min(matches.values_list("time", flat=True))
        self.end = max(matches.values_list("time", flat=True))

    def _get_winrate(self, matches):
        matches = list(matches)
        winrate = sum(1 for m in matches if m.winner) / len(matches) * 100
        return round(winrate, 2)

    @classmethod
    def convert_to_msec_tstamp(cls, date_):
        return int(date_.strftime("%s")) * 1000

    def __str__(self):
        range = (self.end.year - self.start.year) * 12
        range += self.end.month - self.start.month + 1
        start = self.start
        if range > 6:
            start = self.end - relativedelta(months=5)
            range = 6

        return self.html.format(
            class_name="RecentCalenderHeatmap",
            data=self.data,
            domain="month",
            start=self.convert_to_msec_tstamp(start),
            range=range
        )


class StreakCalculator:

    def __init__(self, matches):
        if not matches.exists():
            raise ValueError("matches should not be empty")
        self.matches = list(matches.order_by("time").values_list(
            "winner", flat=True
        ))
        self.result = self._count_wins(self.matches)
        self.winrate = (
            sum(1 for win in self.matches if win) / len(self.matches) * 100
        )
        self.winrate_after_win = (
            self.result[True][True] / sum(self.result[True].values()) * 100
        )
        self.winrate_after_loss = (
            self.result[False][True] / sum(self.result[False].values()) * 100
        )
        self.score = self.winrate_after_win - self.winrate_after_loss

    @classmethod
    def _count_wins(cls, win_list):
        result = {True:  {True: 0, False: 0},
                  False: {True: 0, False: 0}}

        last_win = win_list[0]
        for win in win_list[1:]:
            result[last_win][win] += 1
            last_win = win

        return result

