from rest_framework import serializers, generics
from django.utils import timezone
from django.db.models import Min
from .models import Movie, Showtime, Seat


class MovieSerializer(serializers.ModelSerializer):
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
        ]

    def get_next_showtime(self, obj):
        next_showtime = Showtime.objects.filter(
            movie=obj, start_time__gt=timezone.now()
        ).aggregate(Min("start_time"))["start_time__min"]
        return next_showtime


class SeatSerializer(serializers.ModelSerializer):
    is_booked = serializers.SerializerMethodField()

    class Meta:
        model = Seat
        fields = ["row", "number", "is_booked"]

    def get_is_booked(self, obj):
        showtime = self.context["view"].get_object()
        return showtime.booked_seats().filter(id=obj.id).exists()


class ShowtimeDetailSerializer(serializers.ModelSerializer):
    seats = serializers.SerializerMethodField()

    class Meta:
        model = Showtime
        fields = ["id", "cinema", "movie", "start_time", "end_time", "seats"]

    def get_seats(self, obj):
        seats = Seat.objects.filter(cinema=obj.cinema)
        serializer = SeatSerializer(instance=seats, many=True, context=self.context)
        return serializer.data
