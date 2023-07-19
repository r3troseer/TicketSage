from django.core.management.base import BaseCommand
from base.models import Movie


class Command(BaseCommand):
    help = "Updates movie data from API"

    def handle(self, *args, **options):
        Movie.update_from_api()
        # self.stdout.write(self.style.SUCCESS("Movie data updated successfully."))
