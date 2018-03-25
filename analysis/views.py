from datetime import timedelta, datetime
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from requests import HTTPError

from analysis.analysis import CalendarHeatMap, StreakCalculator
from analysis.models import Calculation
from riot.api import get_summoner
from riot.models import Match
from .tasks import calculate_score


def index(request):
    if request.method == "POST":
        form = SummonerNameForm(request.POST)
        if form.is_valid():
            region = form.cleaned_data["region"]
            summoner_name = form.cleaned_data["summoner_name"]
            summoner = get_summoner(summoner_name, region)
            try:
                calc = Calculation.objects.filter(
                    summoner=summoner,
                    created__gt=datetime.now() - timedelta(days=settings.CALC_DAYS)
                ).latest("created")
                if calc.finished:
                    return redirect("result", calc_id=calc.pk)
                return redirect("wait", calc_id=calc.pk)
            except Calculation.DoesNotExist:
                calc = Calculation.objects.create(summoner=summoner, finished=False)
                calculate_score.delay(summoner.pk, calc.pk)
                return redirect("wait", calc_id=calc.pk)
    else:
        form = SummonerNameForm()

    return render(request, 'analysis/index.html', {
        'form': form,
    })


def wait(request, calc_id):
    return render(request, 'analysis/wait.html', {
        "calc_id": calc_id,
        "form": SummonerNameForm(),
    })


@csrf_exempt
def progress(request, calc_id):
    calc = Calculation.objects.get(pk=calc_id)
    if calc.finished:
        progress = 100
    else:
        progress = min(calc.count / settings.MATCH_LIMIT * 100, 100)
    return JsonResponse({"progress": round(progress, 1)})


def result(request, calc_id):
    calculation = Calculation.objects.get(pk=calc_id)
    matches = Match.objects.filter(summoner=calculation.summoner_id)
    context = {"form": SummonerNameForm(), "summoner": calculation.summoner}
    if matches:
        context["total"] = matches.count()
        context["heatmap"] = CalendarHeatMap(matches)
        context["analysis"] = StreakCalculator(matches)
        calculation.summoner.score = context["analysis"].score
        calculation.summoner.save()

    return render(request, 'analysis/result.html', context)


class SummonerField(forms.RegexField):
    def to_python(self, value):
        return value.lower().replace(" ", "")


class SummonerNameForm(forms.Form):
    url = reverse_lazy("index")

    summoner_name = SummonerField(regex=r'^[0-9\w _\\.]+$')
    region = forms.ChoiceField(choices=settings.REGIONS, initial='euw1')

    def clean(self):
        if 'summoner_name' not in self.cleaned_data:
            raise ValidationError("Please enter a summoner name")
        try:
            get_summoner(
                self.cleaned_data['summoner_name'], self.cleaned_data['region']
            )
        except HTTPError:
            raise ValidationError("Summoner was not found")
        return super().clean()