from django.db import models


class SwitchGameListSlot(models.Model):
    order = models.IntegerField(default=0)


class SwitchGameList(models.Model):
    title = models.CharField(max_length=128)
    query_json = models.CharField(max_length=256)
    logged_list = models.BooleanField(default=False)
    frequency = models.IntegerField()
    slot = models.ForeignKey(SwitchGameListSlot, on_delete=models.CASCADE)
