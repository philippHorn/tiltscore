from django.test import TestCase

# Create your tests here.
from analysis.analysis import StreakCalculator

win_list = [
    True, True, False, False, True
]

long_win_list = [
    True, True, False, False, True, False, False, True, False, True, True,
    False, True, True, False, True, False, True, True, True, True, True, True,
]


class AnalysisTestCase(TestCase):

    def test_streaks(self):
        result = StreakCalculator._count_wins(win_list)
        self.assertEquals(result[True], {True: 1, False: 1})
        self.assertEquals(result[False], {True: 1, False: 1})

    def test_streaks_long(self):
        result = StreakCalculator._count_wins(long_win_list)
        self.assertEquals(result[True], {True: 8, False: 6})
        self.assertEquals(result[False], {True: 6, False: 2})
