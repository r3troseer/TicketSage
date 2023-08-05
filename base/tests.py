from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from dj_rest_auth.models import TokenModel
from .models import Movie, Showtime, Seat, Booking, Cinema
import json


class MovieTestCase(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.token, _ = TokenModel.objects.get_or_create(user=self.user)

        # Create a test cinema
        self.cinema = Cinema.objects.create(
            name="Test Cinema", rows=5, seats_per_row=10
        )

        # Create a test movie
        self.movie = Movie.objects.create(
            title="Test Movie",
            duration=timedelta(hours=2),
            rating=8.5,
            overview="This is a test movie.",
            poster="http://example.com/poster.jpg",
            backdrop_path="http://example.com/backdrop.jpg",
            tmdb_id=12345,
            release_date=timezone.now(),
        )
        # Create a test showtime
        self.showtime = Showtime.objects.create(
            cinema=self.cinema,
            movie=self.movie,
            price=1500,
            start_time="2023-08-07T12:00:00Z",
            end_time="2023-08-07T14:00:00Z",
        )

    def test_movie_list(self):
        response = self.client.get("/movies/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        # Convert the response content to JSON
        data = json.loads(response.content)
        self.assertTrue("next_showtime" in data[0])

    def test_movie_detail(self):
        response = self.client.get(f"/movies/{self.movie.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Movie")


class ShowtimeTestCase(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.token, _ = TokenModel.objects.get_or_create(user=self.user)

        # Create a test cinema
        self.cinema = Cinema.objects.create(
            name="Test Cinema", rows=5, seats_per_row=10
        )

        # Create a test movie
        self.movie = Movie.objects.create(
            title="Test Movie",
            duration=timedelta(hours=2),
            rating=8.5,
            overview="This is a test movie.",
            poster="http://example.com/poster.jpg",
            backdrop_path="http://example.com/backdrop.jpg",
            tmdb_id=12345,
            release_date=timezone.now(),
        )

        # Create a test showtime
        self.showtime = Showtime.objects.create(
            cinema=self.cinema,
            movie=self.movie,
            price=1500,
            start_time="2023-08-06T12:00:00Z",
            end_time="2023-08-06T14:00:00Z",
        )

    def test_showtime_detail(self):
        response = self.client.get(f"/showtimes/{self.showtime.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["cinema"]["name"], "Test Cinema")
        self.assertEqual(response.data["movie"]["title"], "Test Movie")
        self.assertIn("seats", response.data)

    def test_book_showtime(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        seat = Seat.objects.filter(cinema=self.cinema).first()
        response = self.client.patch(
            f"/showtimes/{self.showtime.id}/",
            {"book_seat": [seat.id]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        booking = Booking.objects.filter(showtime=self.showtime, seat=seat).first()
        self.assertIsNotNone(booking)


class UserBookingTestCase(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.token, _ = TokenModel.objects.get_or_create(user=self.user)

        # Create a test cinema
        self.cinema = Cinema.objects.create(
            name="Test Cinema", rows=5, seats_per_row=10
        )

        # Create a test movie
        self.movie = Movie.objects.create(
            title="Test Movie",
            duration=timedelta(hours=2),
            rating=8.5,
            overview="This is a test movie.",
            poster="http://example.com/poster.jpg",
            backdrop_path="http://example.com/backdrop.jpg",
            tmdb_id=12345,
            release_date=timezone.now(),
        )

        # Create a test showtime
        self.showtime = Showtime.objects.create(
            cinema=self.cinema,
            movie=self.movie,
            price=1500,
            start_time="2023-08-06T12:00:00Z",
            end_time="2023-08-06T14:00:00Z",
        )

        # Create a test booking
        self.booking = Booking.objects.create(
            user=self.user,
            showtime=self.showtime,
            seat=self.cinema.seat_set.first(),
            ticket_number="ABC123",
        )

    def test_user_bookings_list(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get("/my-movies/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["ticket_number"], "ABC123")

    def test_cancel_booking(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.delete(f"/my-movies/{self.booking.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Booking.objects.filter(id=self.booking.id).exists())


class RegistrationTestCase(APITestCase):
    def setUp(self):
        self.register_url = reverse("rest_register")
        self.user_data = {
            "username": "newuser",
            "password1": "newtestpassword",
            "password2": "newtestpassword",
            "email": "newuser@example.com",
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, "newuser")
        self.assertTrue(
            User.objects.get().is_active
        )  

    # def test_user_registration_missing_email(self):
    #     # Test registration without providing an email
    #     self.user_data["email"] = ""
    #     response = self.client.post(self.register_url, self.user_data, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #     self.assertEqual(User.objects.count(), 1)
    #     self.assertEqual(User.objects.get().username, "newuser")
    #     self.assertTrue(User.objects.get().is_active)

    def test_user_registration_with_existing_username(self):
        # Create a user with the same username as in self.user_data
        User.objects.create_user(username="newuser", password="existingpassword")
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)  # The existing user is not replaced
        self.assertIn("username", response.data)

    def test_user_registration_with_mismatched_passwords(self):
        # Test registration with mismatched passwords
        self.user_data["password2"] = "differentpassword"
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)  # No user is created
        self.assertIn("non_field_errors", response.data)


class AuthenticationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.token, _ = TokenModel.objects.get_or_create(user=self.user)
        self.login_url = reverse("rest_login")
        self.logout_url = reverse("rest_logout")
        self.password_change_url = reverse("rest_password_change")

    def test_user_login(self):
        data = {"username": "testuser", "password": "testpassword"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("key", response.data)

    def test_user_logout(self):
        # Authenticate the user first
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_password_change(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        data = {
            "old_password": "testpassword",
            "new_password1": "newtestpassword",
            "new_password2": "newtestpassword",
        }
        response = self.client.post(self.password_change_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that the password has been changed successfully
        user = User.objects.get(username="testuser")
        self.assertTrue(user.check_password("newtestpassword"))

    def test_invalid_password_change(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        data = {
            "old_password": "wrongpassword",
            "new_password1": "newtestpassword",
            "new_password2": "newtestpassword",
        }
        response = self.client.post(self.password_change_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["old_password"][0],
            "Your old password was entered incorrectly. Please enter it again.",
        )


class AuthorizationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.token, _ = TokenModel.objects.get_or_create(user=self.user)

    def test_authenticated_access(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get("/movies/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_access(self):
        response = self.client.get("/my-movies/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
