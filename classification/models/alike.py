from django.db import models
from django.contrib.auth import get_user_model

from games.models import SwitchGame


class SuggestAlike(models.Model):
    game1 = models.ForeignKey(
        SwitchGame,
        on_delete=models.CASCADE,
        related_name='suggested_alike_game1',
    )

    game2 = models.ForeignKey(
        SwitchGame,
        on_delete=models.CASCADE,
        related_name='suggested_alike_game2',
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    class Meta:
        unique_together = ('game1', 'game2', 'user')

    def __str__(self):
        return 'User {} voted {} is like {}' \
            .format(self.user, self.game1, self.game2)


class ConfirmedAlike(models.Model):
    NINTENDO = 'NTD'
    SITE_STAFF = 'STF'
    VOTE = 'VOT'

    CONFIRMED_BY_CHOICES = (
        (NINTENDO, 'Nintendo'),
        (SITE_STAFF, 'Site staff'),
        (VOTE, 'Vote'),
    )

    confirmed_by = models.CharField(max_length=3, choices=CONFIRMED_BY_CHOICES)

    game1 = models.ForeignKey(
        SwitchGame, on_delete=models.CASCADE, related_name='alike_game1')

    game2 = models.ForeignKey(
        SwitchGame, on_delete=models.CASCADE, related_name='alike_game2')

    class Meta:
        unique_together = ('game1', 'game2', 'confirmed_by')

    def __str__(self):
        return '{} is like {}'.format(self.game1, self.game2)
