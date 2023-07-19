from datetime import timedelta
from django.conf import settings
from django.db import models, transaction
from decouple import config
import requests
import json
import traceback
import logging

logger = logging.getLogger(__name__)


class Movie(models.Model):
    title = models.CharField(max_length=200)
    duration = models.DurationField()
    rating = models.FloatField()
    poster = models.URLField()
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

            with transaction.atomic():
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
                        duration=timedelta(seconds=movie_details["runtime"]),
                        rating=movie_details["vote_average"],
                        poster="https://image.tmdb.org/t/p/original/" + movie_data["poster_path"],
                        tmdb_id=movie_details["id"],
                        release_date=movie_details["release_date"],
                    )
                    movies.append(movie)

                # Bulk create the new movies in the database
                cls.objects.bulk_create(movies)
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


class Seat(models.Model):
    row = models.IntegerField()
    number = models.IntegerField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.row},{self.number}, {self.is_booked}"


class Booking(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.movie},{self.seat}"


class Cinema(models.Model):
    name = models.CharField(max_length=200)
    rows = models.IntegerField()
    seats_per_row = models.IntegerField()
    movies = models.ManyToManyField(Movie)
    seats = models.ManyToManyField(Seat)

    def __str__(self):
        return self.name
