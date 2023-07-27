from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Booking, Cinema, Movie, Seat, Showtime
from .serializers import (
    MovieListSerializer,
    ShowtimeDetailSerializer,
    MovieDetailSerializer,
    BookingSerializer,
)


# Create your views here.
class MovieListView(generics.ListAPIView):
    """
    API view to retrieve list of all available movies.
    """

    queryset = Movie.objects.all()
    serializer_class = MovieListSerializer


class MovieDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve movie detail and available showtime for the movie
    """

    queryset = Movie.objects.all()
    serializer_class = MovieDetailSerializer


class ShowtimeDetailView(generics.RetrieveUpdateAPIView):
    """
    API view to retrieve or book for a single showtime.
    """

    queryset = Showtime.objects.all()
    serializer_class = ShowtimeDetailSerializer

    def get_serializer_context(self):
        user = self.request.user
        context = super(ShowtimeDetailView, self).get_serializer_context()
        context.update({
            "user": user
            # extra data
        })
        return context


class UserMovieView(generics.ListAPIView):
    """
    API view to retrieve available movie(s) booked by user.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def get_queryset(self):
        user = self.request.user
        return Booking.objects.filter(user=user)
