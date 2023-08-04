from rest_framework import serializers, generics
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from .models import Movie, Showtime, Seat, Booking, Cinema, Payment
import secrets


class MovieListSerializer(serializers.ModelSerializer):
    """
    Serializer for the Movie model. It includes fields for the next showtime and its ID.
    """
    rating=serializers.DecimalField(decimal_places=1, max_digits=3)
    next_showtime = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "duration",
            "rating",
            "poster",
            "release_date",
            "next_showtime",
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
    """
    Serializer for the Movie Detail. It includes fields for the available showtime and its ID.
    """
    rating=serializers.DecimalField(decimal_places=1, max_digits=3)
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
        return ShowtimeSerializer(showtime, many=True, context=self.context).data


class SeatSerializer(serializers.ModelSerializer):
    is_booked = serializers.SerializerMethodField()

    class Meta:
        model = Seat
        fields = [
            "id",
            "seat_number",
            "is_booked",
        ]

    def get_is_booked(self, obj):
        """
        Method to check if a seat is booked for a particular showtime.
        """
        showtime = self.context["view"].get_object()
        return showtime.booked_seats().filter(id=obj.id).exists()


class CinemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cinema
        fields = ["name", "seats_per_row"]


class MovieTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["title", "poster"]


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
        user = self.context.get("user")
        ticket_numbers = [] # Store Ticket number to be returned
        bookings_to_create = []  # Store Booking objects to be created
        validation_errors = []  # Store validation errors to be raised
        for book_seat_id in book_seat_ids:
            try:
                seat = Seat.objects.get(id=book_seat_id)
                if Booking.objects.filter(showtime=instance, seat=seat).exists():
                    validation_errors.append(
                        f"The seat with ID {book_seat_id} is already booked for this showtime."
                    )
                else:
                    bookings_to_create.append(seat)  # Add to the seat list for later booking
            except Seat.DoesNotExist:
                validation_errors.append(
                    f"The seat with ID {book_seat_id} does not exist."
                )
        if validation_errors:
            raise serializers.ValidationError(validation_errors)
        
        # If no validation errors, create the bookings
        for seat in bookings_to_create:
            booking = Booking.objects.create(
                user=user,
                showtime=instance,
                seat=seat,
                ticket_number=secrets.token_hex(5),
            )
            ticket_numbers.append(booking.ticket_number) # Add to the ticket list for booking(s) made

            # Create Payment object and associate it with the booking
            payment = Payment.objects.create(
                booking=booking,
                amount=booking.showtime.price,
                paid=False,
            )

        instance.ticket_numbers = ticket_numbers
        return instance

    def to_representation(self, instance):
        """
        Method to include the booking IDs in the serialized output.
        """
        representation = super().to_representation(instance)
        representation["ticket_numbers"] = getattr(instance, "ticket_numbers", [])
        return representation


class SeatBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = [
            "id",
            "seat_number",
        ]


class ShowtimebookSerializer(serializers.ModelSerializer):
    movie = MovieTitleSerializer(read_only=True)
    cinema = CinemaSerializer(read_only=True)

    class Meta:
        model = Showtime
        fields = ["id", "movie", "cinema", "start_time"]


class BookingSerializer(serializers.ModelSerializer):
    showtime = ShowtimebookSerializer(read_only=True)
    seat = SeatBookSerializer()

    class Meta:
        model = Booking
        fields = ["id", "showtime", "seat", "ticket_number"]


# class UserSerializer(serializers.ModelSerializer):
#     first_name = serializers.CharField(required=True)
#     last_name = serializers.CharField(required=True)
#     cinema = CinemaSerializer(read_only=True)


#     class Meta:
#         model = User
#         fields = ['id', 'first_name', 'last_name', ]
