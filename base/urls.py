from django.urls import path
from . import views
from .views import MovieListView, ShowtimeDetailView, MovieDetailView, UserMovieView

urlpatterns=[
    path('movies/', MovieListView.as_view(), name='movie-list'),
    path('my-movies/', UserMovieView.as_view(), name='my-movies'),
    path('movies/<int:pk>/', MovieDetailView.as_view(), name='movie-detail'),
    path('showtimes/<int:pk>/', ShowtimeDetailView.as_view(), name='showtime-detail'),
]
