from django.db import models

from . import SwitchGameUS, SwitchGameEU


class SwitchGame(models.Model):
    game_us = models.OneToOneField(
        SwitchGameUS,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    game_eu = models.OneToOneField(
        SwitchGameEU,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    game_code_unique = models.CharField(max_length=5, unique=True)
    hide = models.BooleanField(default=False)

    @property
    def title(self):
        return self.game_eu.title if self.game_eu else self.game_us.title

    def __str__(self):
        return self.game_code_unique
