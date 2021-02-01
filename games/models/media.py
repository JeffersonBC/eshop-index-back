from django.db import models

from games.models import SwitchGame


class SwitchGameMedia(models.Model):
    IMAGE_URL = 'IMG'
    YOUTUBE_CODE = 'YTB'

    CONFIRMED_BY_CHOICES = (
        (IMAGE_URL, 'Image URL'),
        (YOUTUBE_CODE, 'YouTube video code'),
    )

    media_type = models.CharField(max_length=3, choices=CONFIRMED_BY_CHOICES)
    url = models.CharField(max_length=256)
    game = models.ForeignKey(SwitchGame, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
