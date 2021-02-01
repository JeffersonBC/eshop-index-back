from django.db import models

from games.models import SwitchGame


class SwitchGamePrice(models.Model):
    game = models.ForeignKey(SwitchGame, on_delete=models.CASCADE)
    country = models.CharField(max_length=2)

    amount = models.CharField(max_length=12)
    currency = models.CharField(max_length=8)
    raw_value = models.FloatField()

    class Meta:
        unique_together = ('game', 'country')


class SwitchGameSale(models.Model):
    game = models.ForeignKey(SwitchGame, on_delete=models.CASCADE)
    country = models.CharField(max_length=2)

    amount = models.CharField(max_length=12)
    currency = models.CharField(max_length=8)
    raw_value = models.FloatField()

    start_datetime = models.DateTimeField(null=True, blank=True)
    end_datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('game', 'country')
