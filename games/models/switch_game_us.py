from django.db import models


class SwitchGameUS(models.Model):
    # Game Info
    title = models.CharField(max_length=256)
    slug = models.SlugField()
    release_date = models.DateField()

    # Id
    nsuid = models.CharField(max_length=14, null=True, blank=True)
    game_code_system = models.CharField(max_length=3)
    game_code_region = models.CharField(max_length=1)
    game_code_unique = models.CharField(max_length=5, unique=True)

    # Media
    front_box_art = models.URLField()
    video_link = models.CharField(max_length=32, null=True, blank=True)

    @property
    def game_code(self):
        return (
            self.game_code_system +
            self.game_code_region +
            self.game_code_unique
        )

    def __str__(self):
        return '[{}] {}'.format(self.game_code, self.title)

    # *** TAG CANDIDATES ***

    # free_to_start = models.BooleanField(verbose_name="Free to start")
    # categories
    # number_of_players = models.CharField(verbose_name="Number of players",
    #     max_length=126)

    # *** UNUSED/ REDUNDANT INFO ***

    # buyitnow = models.BooleanField(verbose_name="Buy it now")
    # buyonline = models.BooleanField(verbose_name="Buy online")
    # digitaldownload = models.BooleanField(verbose_name="Digital download")
    # id = models.CharField(verbose_name="Hash Id", max_length=32)
    # system = models.CharField(verbose_name="System", max_length=126)

    # eshop_price = models.DecimalField(
    #   verbose_name="USA eShop price (in dollars)",
    #   max_digits=5,
    #   decimal_places=2
    # )
    # ca_price = models.DecimalField(
    #   verbose_name="Canada eShop price (in canadian dollars)",
    #   max_digits=5,
    #   decimal_places=2
    # )
