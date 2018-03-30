from django.db import models
from django.db.models import Window, F
from django.db.models.functions import PercentRank


class Summoner(models.Model):
    name = models.CharField(max_length=30)
    display_name = models.CharField(max_length=30)
    riot_id = models.BigIntegerField()
    region = models.CharField(max_length=5)
    account_id = models.BigIntegerField()
    score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} region: {self.region}"

    @property
    def tilt_rank(self):
        """return percentage rank in score compared to all summoners"""
        qset = Summoner.objects.annotate(
            rank=Window(
                expression=PercentRank(),
                order_by=F("score").asc())
        ).values("pk", "rank")

        raw_query = "SELECT * FROM ({subquery}) as x WHERE id={id}".format(
            subquery=qset.query,
            id=self.id,
        )
        return Summoner.objects.raw(raw_query)[0].rank * 100

    class Meta:
        unique_together = ('name', 'region')


class Match(models.Model):
    """contains information about one summoner from one match"""
    riot_id = models.BigIntegerField()
    time = models.DateTimeField()
    summoner = models.ForeignKey(Summoner, on_delete=models.CASCADE)
    queue_type = models.CharField(max_length=30)
    winner = models.BooleanField()
    role = models.CharField(max_length=30, null=True)
    lane = models.CharField(max_length=30, null=True)

    def __str__(self):
        return f"{self.riot_id} of {self.summoner.name}"

    class Meta:
        unique_together = ('riot_id', 'summoner')
