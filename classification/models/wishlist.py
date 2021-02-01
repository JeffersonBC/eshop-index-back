from django.db import models
from django.contrib.auth import get_user_model

from games.models import SwitchGame


class Wishlist(models.Model):
    game = models.ForeignKey(SwitchGame, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('game', 'user')

    def __str__(self):
        return '{} wishes [{}]'.format(self.user, self.game)
