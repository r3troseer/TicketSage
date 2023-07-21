from django.urls import path
from . import views
from .views import MovieListView, ShowtimeDetailView

urlpatterns=[
    path('movies/', MovieListView.as_view(), name='movie-list'),
    path('showtimes/<int:pk>/', ShowtimeDetailView.as_view(), name='showtime-detail'),
    path('movies_html/', views.movie_list, name='movie_list'),
    path('seats/', views.seat_list, name='seat_list'),
    path('cinemas/<int:pk>/', views.cinema_detail, name='cinema_detail'),
    path('bookings/new/', views.new_booking, name='new_booking'),
    path('bookings/<int:pk>/', views.booking_detail, name='booking_detail'),
]
