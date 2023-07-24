from rest_framework import serializers, generics
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Movie, Showtime, Seat, Booking, Cinema
import secrets


class MovieSerializer(serializers.ModelSerializer):
    """
    Serializer for the Movie model. It includes fields for the next showtime and its ID.
    """

    next_showtime = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            "title",
            "duration",
            "rating",
            "poster",
            # "tmdb_id",
            "release_date",
            "next_showtime",
            # "next_showtime_id"
        ]

    def get_next_showtime(self, obj):
        """
        Method to get the next showtime for the movie.
        """
        next_showtime = (
            Showtime.objects.filter(movie=obj, start_time__gt=timezone.now())
            .order_by("start_time")
            .first()
        )
        return next_showtime.start_time


class ShowtimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Showtime
        fields = ["id", "start_time"]


class MovieDetailSerializer(serializers.ModelSerializer):
    showtimes = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            "title",
            "overview",
            "duration",
            "rating",
            "backdrop_path",
            "poster",
            "release_date",
            "showtimes",
        ]

    def get_showtimes(self, obj):
        """
        Method to get showtimes for the movie.
        """
        showtime = Showtime.objects.filter(
            movie=obj, start_time__gt=timezone.now()
        ).order_by("start_time")
        print(showtime)
        return ShowtimeSerializer(showtime, many=True, context=self.context).data


class SeatSerializer(serializers.ModelSerializer):
    is_booked = serializers.SerializerMethodField()

    class Meta:
        model = Seat
        fields = ["id", "row", "number", "is_booked"]

    def get_is_booked(self, obj):
        """
        Method to check if a seat is booked for a particular showtime.
        """
        showtime = self.context["view"].get_object()
        return showtime.booked_seats().filter(id=obj.id).exists()


class CinemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cinema
        fields = ["name"]


class MovieTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["title"]


class ShowtimeDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for the Showtime model. It includes a field for booking seats.
    """

    seats = serializers.SerializerMethodField()
    book_seat = serializers.ListField(child=serializers.IntegerField(), required=False)
    cinema = CinemaSerializer(read_only=True)
    movie = MovieTitleSerializer(read_only=True)

    class Meta:
        model = Showtime
        fields = [
            "id",
            "movie",
            "cinema",
            "start_time",
            "end_time",
            "seats",
            "book_seat",
        ]
        read_only_fields = ["start_time", "end_time"]

    def get_seats(self, obj):
        """
        Method to get all seats for a cinema.
        """
        seats = Seat.objects.filter(cinema=obj.cinema)
        return SeatSerializer(seats, many=True, context=self.context).data

    def update(self, instance, validated_data):
        """
        Method to handle the booking of seats.
        """
        book_seat_ids = validated_data.pop("book_seat", [])
        booking_ids = []
        for book_seat_id in book_seat_ids:
            try:
                seat = Seat.objects.get(id=book_seat_id)
            except Seat.DoesNotExist:
                raise serializers.ValidationError(
                    f"The seat with ID {book_seat_id} does not exist."
                )
            if Booking.objects.filter(showtime=instance, seat=seat).exists():
                raise serializers.ValidationError(
                    f"The seat with ID {book_seat_id} is already booked for this showtime."
                )
            booking = Booking.objects.create(
                showtime=instance, seat=seat, booking_id=secrets.token_hex(5)
            )
            booking_ids.append(booking.booking_id)
        instance.booking_ids = booking_ids
        return instance

    def to_representation(self, instance):
        """
        Method to include the booking IDs in the serialized output.
        """
        representation = super().to_representation(instance)
        representation["booking_ids"] = getattr(instance, "booking_ids", [])
        return representation


# class BookingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Booking
#         fields = []


# class UserSerializer(serializers.ModelSerializer):
#     first_name = serializers.CharField(required=True)
#     last_name = serializers.CharField(required=True)
#     cinema = CinemaSerializer(read_only=True)


#     class Meta:
#         model = User
#         fields = ['id', 'first_name', 'last_name', ]

