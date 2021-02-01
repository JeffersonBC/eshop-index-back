from django.db import models
from django.contrib.auth import get_user_model

from games.models import SwitchGame
from .recomendation import Recomendation


class Review(models.Model):
    review_text = models.TextField()
    game = models.ForeignKey(SwitchGame, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    recomendation = models.OneToOneField(
        Recomendation, on_delete=models.CASCADE)

    post_date = models.DateTimeField(auto_now_add=True)
    last_update_date = models.DateTimeField(auto_now=True)
    has_edited = models.BooleanField(default=False)

    class Meta:
        unique_together = ('game', 'user')

    def __str__(self):
        return '{} review, by {}'.format(self.game, self.user)


class VoteReview(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    vote = models.BooleanField()

    class Meta:
        unique_together = ('review', 'user')

    def __str__(self):
        return '{} - {} by {}'.format(self.review, self.vote, self.user)
