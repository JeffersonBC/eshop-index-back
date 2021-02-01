from django.db import models
from django.contrib.auth import get_user_model

from games.models import SwitchGame


class TagGroup(models.Model):
    name = models.CharField(max_length=64, unique=True)
    allow_vote = models.BooleanField(default=True)
    min_games_for_search = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=128)
    tag_group = models.ForeignKey(
        TagGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ('name', 'tag_group')

    def __str__(self):
        return self.name


class SuggestedTag(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    game = models.ForeignKey(SwitchGame, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    value = models.BooleanField(default=True)

    class Meta:
        unique_together = ('tag', 'game', 'user')

    def __str__(self):
        return '[{}] {} - {}, by {}'.format(
            self.game, self.tag, self.value, self.user)


class ConfirmedTag(models.Model):
    NINTENDO = 'NTD'
    SITE_STAFF = 'STF'
    VOTE = 'VOT'

    CONFIRMED_BY_CHOICES = (
        (NINTENDO, 'Nintendo'),
        (SITE_STAFF, 'Site staff'),
        (VOTE, 'Vote'),
    )

    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    game = models.ForeignKey(SwitchGame, on_delete=models.CASCADE)
    confirmed_by = models.CharField(max_length=3, choices=CONFIRMED_BY_CHOICES)

    class Meta:
        unique_together = ('tag', 'game', 'confirmed_by')

    def __str__(self):
        return '[{}] {} - {}'.format(self.game, self.tag, self.confirmed_by)
