from analysis.models import Calculation
from riot.api import get_latest_matches
from riot.models import Summoner
from tilt.celery import app

@app.task
def calculate_score(summoner_id, calculation_id):
    summoner = Summoner.objects.get(pk=summoner_id)
    calculation = Calculation.objects.get(pk=calculation_id)
    num_matches = 0
    for match in get_latest_matches(summoner):
        num_matches += 1
        if num_matches % 5 == 0:
            calculation.count = num_matches
            calculation.save()
    calculation.finished = True
    calculation.save()