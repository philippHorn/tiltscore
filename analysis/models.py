from django.db import models
from riot.models import Summoner


class Calculation(models.Model):
    summoner = models.ForeignKey(Summoner, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    count = models.IntegerField(default=0)
    finished = models.BooleanField()
