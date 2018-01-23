from django.test import TestCase

from riot.api import get_summoner, get_match_list, get_match, get_latest_matches
from riot.models import Summoner, Match


class RiotTestCase(TestCase):

    def test_summoner(self):
        summoner = get_summoner("mogl", "euw1")
        self.assertTrue(Summoner.objects.filter(name="mogl").exists())

    def test_match_list(self):
        summoner = get_summoner("mogl", "euw1")
        match_list = get_match_list(summoner)
        self.assertTrue(match_list)

    def test_get_match_info(self):
        summoner = get_summoner("mogl", "euw1")
        match_list = get_match_list(summoner)
        match = get_match(summoner, match_list[0]["gameId"])
        self.assertTrue(Match.objects.filter(
            summoner__name="mogl",
            riot_id=match.riot_id
        ).exists())

    def test_get_latest_matches(self):
        summoner = get_summoner("mogl", "euw1")
        matches = list(get_latest_matches(summoner, limit=10))
        self.assertEquals(matches, sorted(matches, key=lambda m: m.time))
