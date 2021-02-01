from django.core.management.base import BaseCommand

from games.tasks import update_switch_us_free_tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        update_switch_us_free_tag()
