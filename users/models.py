from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser


class EshopIndexUser(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True,
        db_index=True
    )


class Following(models.Model):
    follower = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='follower'
    )

    followed = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='followed',
    )

    class Meta:
        unique_together = ('follower', 'followed')

    def __str__(self):
        return '{} following {}'.format(self.follower.first_name,
                                        self.followed.first_name)
