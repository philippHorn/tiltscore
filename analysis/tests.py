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
        wins, losses = StreakCalculator._count_wins(win_list)
        self.assertEquals(wins, {2: 1, 1: 1})
        self.assertEquals(losses, {2: 1})

    def test_streaks_long(self):
        wins, losses = StreakCalculator._count_wins(long_win_list)
        self.assertEquals(wins, {2: 3, 1: 3, 6: 1})
        self.assertEquals(losses, {1: 4, 2: 2})