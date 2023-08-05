from django.urls import path
from . import views
from .views import MovieListView, ShowtimeDetailView, MovieDetailView, UserMovieListView, UserMovieDestroyView

urlpatterns=[
    path('movies/', MovieListView.as_view(), name='movie-list'),
    path('my-movies/', UserMovieListView.as_view(), name='my-movies'),
    path('my-movies/<int:pk>/', UserMovieDestroyView.as_view(), name='my-movie-destroy'),
    path('movies/<int:pk>/', MovieDetailView.as_view(), name='movie-detail'),
    path('showtimes/<int:pk>/', ShowtimeDetailView.as_view(), name='showtime-detail'),
]
