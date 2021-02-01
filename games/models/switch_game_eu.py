from django.db import models


class SwitchGameEU(models.Model):
    # Game Info
    title = models.CharField(max_length=256)
    url = models.CharField(max_length=256)
    release_date = models.DateField()

    description = models.TextField(null=True, blank=True)

    # Id
    nsuid = models.CharField(max_length=14, null=True, blank=True)
    fs_id = models.CharField(max_length=8)

    game_code_system = models.CharField(max_length=3)
    game_code_region = models.CharField(max_length=1)
    game_code_unique = models.CharField(max_length=5, unique=True)

    # Media
    image_carousel_url = models.CharField(max_length=256)
    image_detail_page_url = models.CharField(max_length=256)
    image_wishlist_url = models.CharField(max_length=256)

    image_url = models.CharField(max_length=256)
    image_sq_url = models.CharField(max_length=256)
    image_sq_h2_url = models.CharField(max_length=256)

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

    # Developer
    # developer = models.CharField(max_length=64)
    # publisher = models.CharField(max_length=64, null=True, blank=True)
    # copyright = models.TextField(null=True, blank=True)

    # add_on_content_b = models.BooleanField()
    # age_rating_sorting_i = models.PositiveSmallIntegerField()
    # age_rating_type = models.CharField(max_length=16)
    # age_rating_value = models.CharField(max_length=4)
    # compatible_controller = models.CharField(max_length=32)
    # {string[]} game_categories_txt
    # {string[]} game_category
    # game_series_t = models.CharField(max_length=8)
    # {string[]} language_availability
    # near_field_comm_b = models.BooleanField()
    # physical_version_b = models.BooleanField()
    # play_mode_handheld_mode_b = models.BooleanField(default=False)
    # play_mode_tabletop_mode_b = models.BooleanField(default=False)
    # play_mode_tv_mode_b = models.BooleanField(default=False)
    # players_from = models.PositiveSmallIntegerField()
    # players_to = models.PositiveSmallIntegerField()

    # *** UNUSED/ REDUNDANT INFO ***

    # change_date = models.DateField()
    # club_nintendo = models.BooleanField()
    # date_from = models.DateField()
    # gift_finder_description_s = models.CharField(max_length=256)
    # gift_finder_detail_page_store_link_s = models.URLField()
    # image_url_tm_s = models.URLField()
    # originally_for_t = models.CharField(max_length=4)
    # pretty_agerating_s = models.CharField(max_length=4)
    # priority = models.DateField()
    # sorting_title = models.CharField(max_length=256)
    # system_names_txt = models.CharField(max_length=64)
    # system_type = models.CharField(max_length=64)
    # title_extras_txt = models.CharField(max_length=256)
    # type = models.CharField(max_length=16)
