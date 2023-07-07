from django.contrib import admin
from .models import Booking, Cinema, Movie, Seat

admin.site.register(Booking)
admin.site.register(Cinema)
admin.site.register(Movie)
admin.site.register(Seat)
