from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from base.models import Showtime, Cinema, Movie, Booking

class Command(BaseCommand):
    help = 'Schedule showtimes for all available movies in the cinema.'

    # def add_arguments(self, parser):
    #     parser.add_argument('--days', type=int, default=7, help='Number of days to schedule showtimes.')
    #     parser.add_argument('--interval', type=int, default=3, help='Interval between consecutive showtimes in hours.')

    def handle(self, *args, **options):
        cinema = Cinema.objects.first()  # Change this to get the desired cinema for scheduling showtimes
        # start_date = timezone.now().date()
        # days = options['days']
        # interval = options['interval']

        Showtime.objects.all().delete()  # Clear existing showtimes before scheduling

        Showtime.create_showtimes(cinema)

        self.stdout.write(self.style.SUCCESS('Showtimes have been scheduled successfully.'))
