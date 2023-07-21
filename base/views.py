from rest_framework import generics, status
from django.shortcuts import render, redirect, get_object_or_404
from .models import Booking, Cinema, Movie, Seat, Showtime
from .forms import BookingForm
from .serializers import MovieSerializer,ShowtimeDetailSerializer


# Create your views here.
class MovieListView(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

class ShowtimeDetailView(generics.RetrieveAPIView):
    queryset = Showtime.objects.all()
    serializer_class = ShowtimeDetailSerializer

def movie_list(request):
    movies = Movie.objects.all()
    return render(request, "movie_list.html", {"movies": movies})


def seat_list(request):
    seats = Seat.objects.all()
    return render(request, "seat_list.html", {"seats": seats})


def cinema_detail(request, pk):
    cinema = get_object_or_404(Cinema, pk=pk)
    return render(request, "cinema_detail.html", {"cinema": cinema})


def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, "booking_detail.html", {"booking": booking})


def new_booking(request):
    if request.method == "POST":
        form = BookingForm(request.POST)

        if form.is_valid():
            # Retrieve the seat and novie from the form's cleaned data
            seat = form.cleaned_data["seat"]
            movie=form.cleaned_data["movie"]
            seat.is_booked = True
            seat.save()
            # Create a new booking instance with the selected movie and seat
            booking = Booking(movie=movie, seat=seat)
            booking.save()
            return redirect("booking_detail", pk=booking.pk)
    else:
        form = BookingForm()

    return render(request, "booking_edit.html", {"form": form})
