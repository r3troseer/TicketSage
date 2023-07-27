from collections import deque
from datetime import timedelta
from django.contrib.auth.models import User
from django.db import models, transaction
from django.utils import timezone
from datetime import timedelta
from decouple import config
import json
import logging
import requests
import secrets

logger = logging.getLogger(__name__)

def number_to_alphabet(num):
    if num < 1 or num > 26:
        raise ValueError("Number should be between 1 and 26.")
    return chr(num + 96)

class Movie(models.Model):
    title = models.CharField(max_length=200)
    duration = models.DurationField()
    rating = models.FloatField()
    overview = models.TextField()
    poster = models.URLField()
    backdrop_path = models.URLField()
    tmdb_id = models.IntegerField()
    release_date = models.DateField()

    def __str__(self):
        return self.title

    @classmethod
    def update_from_api(cls):
        """
        Updates the movie data by fetching the latest information from TMDB API and replacing the existing data in the database.
        """
        try:
            # API endpoint URL
            url = "https://api.themoviedb.org/3/movie/now_playing?region=us%2Cng"
            tmdb_key = config("TMDB_KEY")
            headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {tmdb_key}",
            }

            # Fetch movie data from the API
            response = requests.get(url, headers=headers)
            data = json.loads(response.text)

            # Handle API response errors
            if "results" not in data:
                error_message = data["status_message"]
                raise Exception(f"API error: {error_message}")

            with transaction.atomic():  # ensures that the database operations (deleting existing movies and creating new movies) are executed within a transaction
                # Delete existing movies from the database
                cls.objects.all().delete()

                movies = []
                for movie_data in data["results"]:
                    # Get the TMDB ID for the movie
                    tmdb_id = movie_data["id"]

                    # API URL to fetch the details of the movie
                    movie_details_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
                    response_details = requests.get(movie_details_url, headers=headers)
                    movie_details = json.loads(response_details.text)

                    # Create new Movie instances with API data
                    movie = cls(
                        title=movie_details["original_title"],
                        duration=timedelta(minutes=movie_details["runtime"]),
                        rating=movie_details["vote_average"],
                        poster="https://image.tmdb.org/t/p/original"
                        + movie_data["poster_path"],
                        backdrop_path="https://image.tmdb.org/t/p/original"
                        + movie_data["backdrop_path"],
                        overview=movie_details["overview"],
                        tmdb_id=movie_details["id"],
                        release_date=movie_details["release_date"],
                    )

                    logger.info(f'{movie.title} - gotten')
                    movie.save()  # Save the movie instance to the database
                    movies.append(movie)

                # Get all cinemas
                cinemas = Cinema.objects.all()

                # Add all movies to all cinemas
                for cinema in cinemas:
                    cinema.movies.add(*movies)

                logger.info("Movies updated successfully.")
        except requests.exceptions.Timeout:
            # Handle timeout errors
            logger.exception("Timeout error occurred.")

        except requests.exceptions.RequestException as e:
            # Handle other request-related errors
            logger.exception("Request error occurred:")

        except Exception as e:
            # Handle other exceptions (e.g., API response errors)
            logger.exception("Error occurred:")

    @staticmethod
    def update_movies_from_api(modeladmin, request, queryset):
        """
        Custom admin action to update movies from the API.
        """
        Movie.update_from_api()
        modeladmin.message_user(request, "Movies updated successfully.")

    class Meta:
        verbose_name_plural = "Movies"


class Cinema(models.Model):
    name = models.CharField(max_length=200)
    rows = models.IntegerField()
    seats_per_row = models.IntegerField()
    movies = models.ManyToManyField(Movie, blank=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            seats = [
                Seat.objects.create(cinema=self, row=i, number=j)
                for i in range(1, self.rows + 1)
                for j in range(1, self.seats_per_row + 1)
            ]

    def __str__(self):
        return self.name


class Seat(models.Model):
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE)
    row = models.IntegerField()
    number = models.IntegerField()
    # is_booked = models.BooleanField(default=False)

    @property
    def seat_number(self):
        seat_number=f'{self.number} {number_to_alphabet(self.row)}'
        return seat_number

    def __str__(self):
        return f"{self.row},{self.number}"


class Showtime(models.Model):
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    price = models.IntegerField(default=1500, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.movie} at {self.cinema} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    @classmethod
    def create_showtimes(cls, cinema):
        """
        Schedules showtimes for movies in the given cinema for the next 7 days.
        """
        # Get all available movies
        movies = deque(cinema.movies.all())

        # Start scheduling from tomorrow 8am
        start_time = timezone.now().replace(
            hour=8, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)

        # Schedule for the next 7 days
        for _ in range(7):
            while movies:
                movie = movies.popleft()  # Get the next movie from the queue

                # Calculate end time of the movie
                end_time = start_time + movie.duration

                # If the end time is before 10pm, schedule the movie
                if end_time.hour < 22:
                    cls.objects.create(
                        cinema=cinema,
                        movie=movie,
                        start_time=start_time,
                        end_time=end_time,
                    )

                    # Schedule the next movie 1 hour after the end of the current movie
                    start_time = end_time + timedelta(hours=1)
                else:
                    # If the movie can't be scheduled today, put it back into the queue
                    movies.append(movie)
                    break  # Break the loop and move to the next day

            # Move to the next day 8am
            start_time = start_time.replace(
                hour=8, minute=0, second=0, microsecond=0
            ) + timedelta(days=1)

            # If all movies have been scheduled, start scheduling from the first movie again
            if not movies:
                movies = deque(cinema.movies.all())

    def booked_seats(self):
        return Seat.objects.filter(booking__showtime=self)


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    ticket_number = models.CharField(
        max_length=10, default=secrets.token_hex(5), unique=True
    )
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} with {self.ticket_number} at {self.showtime} - {self.seat}"
