from datetime import timezone, datetime
from functools import wraps

import math
import time
import requests
from django.core.exceptions import ObjectDoesNotExist
from riotwatcher import RiotWatcher
from django.conf import settings

from riot.constants import RELEVANT_QUEUES
from riot.models import Summoner, Match

_api = RiotWatcher(settings.RIOT_API_KEY)

SUMMONER_MAPPING = {
    "name": "name",
    "riot_id": "id",
    "account_id": "accountId",
}
PARTICIPANT_MAPPING = {
    "name": "summonerName",
    "riot_id": "summonerId",
    "account_id": "currentAccountId",
}


def db_cache(db_getter):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return db_getter(*args, **kwargs)
            except ObjectDoesNotExist:
                return func(*args, **kwargs)
        return wrapper
    return decorator


def exponential_retries(wait_time_base, retries=8):
    for i in range(retries):
        yield wait_time_base * (i**2)


def catch_errors(func):
    def wrapped(*args, **kwargs):
        for retry_time in exponential_retries(1):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code not in [429, 503]:
                    raise
            time.sleep(retry_time)
    return wrapped


@db_cache(lambda name, region: Summoner.objects.get(name=name, region=region))
@catch_errors
def get_summoner(name, region):
    summoner_json = _api.summoner.by_name(region, name)
    return create_summoner(summoner_json, SUMMONER_MAPPING, region)


def create_summoner(summoner_json, mapping, region):
    return Summoner.objects.update_or_create(
        region=region,
        name=summoner_json[mapping['name']],
        defaults={"riot_id": summoner_json[mapping['riot_id']]},
        account_id=summoner_json[mapping["account_id"]],
    )[0]


@db_cache(lambda summoner, match_id: Match.objects.get(summoner__region=summoner.region,
                                                       riot_id=match_id))
@catch_errors
def get_match(summoner, match_id):
    try:
        match_json = _api.match.by_id(summoner.region, match_id)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return None
        raise
    try:
        participant_id = next(
            p["participantId"] for p in match_json["participantIdentities"]
            if p["player"]["currentAccountId"] == summoner.account_id
        )
        participant_json = next(p for p in match_json["participants"]
                                if p["participantId"] == participant_id)
    except StopIteration:
        raise ValueError("Summoner does not belong to match")
    for json_ in match_json["participantIdentities"]:
        create_summoner(json_["player"], PARTICIPANT_MAPPING, summoner.region)
    return Match.objects.create(
        summoner=summoner,
        riot_id=match_json["gameId"],
        time=datetime.fromtimestamp(match_json["gameCreation"] / 1000, tz=timezone.utc),
        queue_type=match_json["gameType"],
        winner=participant_json["stats"]["win"],
    )


@catch_errors
def get_matchlist(summoner, begin_index, end_index):
    return _api.match.matchlist_by_account(
        summoner.region,
        summoner.account_id,
        begin_index=begin_index,
        end_index=end_index,
    )


def get_latest_matches(
        summoner,
        limit=settings.MATCH_LIMIT,
        queues=RELEVANT_QUEUES):
    """stream matches from summoner till limit is reached"""

    end_index = 0
    while True:
        try:
            matches = get_matchlist(
                summoner,
                begin_index=end_index,
                end_index=end_index + settings.MATCH_LIST_LIMIT,
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                break
            raise
        yield from (get_match(summoner, match['gameId'])
                    for match in matches["matches"]
                    if match and match["queue"] in queues)
        end_index = matches["endIndex"]

        if end_index >= limit or end_index >= matches["totalGames"]:
            break
