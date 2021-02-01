from django.db import models
from django.contrib.auth import get_user_model

from games.models import SwitchGame


class Recomendation(models.Model):
    game = models.ForeignKey(SwitchGame, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    recomends = models.BooleanField()
    date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('game', 'user')

    def __str__(self):
        return '[{}] {} recomends: {}'.format(
            self.game, self.user, self.recomends)


class ConfirmedHighlight(models.Model):
    SITE_STAFF = 'STF'
    VOTE = 'VOT'

    CONFIRMED_BY_CHOICES = (
        (SITE_STAFF, 'Site staff'),
        (VOTE, 'Vote'),
    )

    confirmed_by = models.CharField(max_length=3, choices=CONFIRMED_BY_CHOICES)
    game = models.ForeignKey(SwitchGame, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('game', 'confirmed_by')

    def __str__(self):
        return '{} is highlighted'.format(self.game)
