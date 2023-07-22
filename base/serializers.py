from rest_framework import serializers, generics
from django.utils import timezone
from django.db.models import Min
from .models import Movie, Showtime, Seat, Booking, Cinema
import secrets

class MovieSerializer(serializers.ModelSerializer):
    next_showtime_id = serializers.SerializerMethodField()
    next_showtime = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            "title",
            "duration",
            "rating",
            "poster",
            "tmdb_id",
            "release_date",
            "next_showtime",
            "next_showtime_id"
        ]

    def get_next_showtime(self, obj):
        next_showtime = Showtime.objects.filter(
            movie=obj, start_time__gt=timezone.now()
        ).order_by('start_time').first()
        return next_showtime.start_time
    
    def get_next_showtime_id(self, obj):
        next_showtime = Showtime.objects.filter(
            movie=obj, start_time__gt=timezone.now()
        ).order_by('start_time').first()
        return next_showtime.id 


class SeatSerializer(serializers.ModelSerializer):
    is_booked = serializers.SerializerMethodField()

    class Meta:
        model = Seat
        fields = ['id',"row", "number", "is_booked"]

    def get_is_booked(self, obj):
        showtime = self.context["view"].get_object()
        return showtime.booked_seats().filter(id=obj.id).exists()


class CinemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cinema
        fields = ['name']

class MovieTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['title']

class ShowtimeDetailSerializer(serializers.ModelSerializer):
    seats = serializers.SerializerMethodField()
    book_seat = serializers.ListField(child=serializers.IntegerField(), required=False)
    cinema = CinemaSerializer(read_only=True)
    movie = MovieTitleSerializer(read_only=True)

    class Meta:
        model = Showtime
        fields = ['id', 'movie', 'cinema', 'start_time', 'end_time', 'seats', 'book_seat']
        read_only_fields = ['start_time', 'end_time']

    def get_seats(self, obj):
        seats = Seat.objects.filter(cinema=obj.cinema)
        return SeatSerializer(seats, many=True, context=self.context).data

    def update(self, instance, validated_data):
        book_seat_ids = validated_data.pop('book_seat', [])
        booking_ids = []
        for book_seat_id in book_seat_ids:
            try:
                seat = Seat.objects.get(id=book_seat_id)
            except Seat.DoesNotExist:
                raise serializers.ValidationError(f'The seat with ID {book_seat_id} does not exist.')
            if Booking.objects.filter(showtime=instance, seat=seat).exists():
                raise serializers.ValidationError(f'The seat with ID {book_seat_id} is already booked for this showtime.')
            booking = Booking.objects.create(showtime=instance, seat=seat, booking_id=secrets.token_hex(5))
            booking_ids.append(booking.booking_id)
        instance.booking_ids = booking_ids
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['booking_ids'] = getattr(instance, 'booking_ids', [])
        return representation
