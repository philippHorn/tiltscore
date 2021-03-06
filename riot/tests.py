from django.test import TestCase

from riot.api import get_summoner, get_matchlist, get_match, get_latest_matches
from riot.models import Summoner, Match


class RiotTestCase(TestCase):

    def test_summoner(self):
        summoner = get_summoner("mogl", "euw1")
        self.assertTrue(Summoner.objects.filter(name="mogl").exists())

    def test_match_list(self):
        summoner = get_summoner("mogl", "euw1")
        match_list = get_matchlist(summoner)
        self.assertTrue(match_list)

    def test_get_match(self):
        summoner = get_summoner("mogl", "euw1")
        match_list = get_matchlist(summoner)
        match = get_match(summoner, match_list['matches'][0]["gameId"])
        self.assertTrue(Match.objects.filter(
            summoner__name="mogl",
            riot_id=match.riot_id
        ).exists())

    def test_get_latest_matches(self):
        summoner = get_summoner("mogl", "euw1")
        matches = list(get_latest_matches(summoner, limit=10))
        sorted_matches = sorted(matches, key=lambda m: m.time, reverse=True)
        self.assertEquals(matches, sorted_matches)
