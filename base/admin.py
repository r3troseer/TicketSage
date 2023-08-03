from django.contrib import admin
from .models import Booking, Cinema, Movie, Seat, Showtime, Payment

admin.site.register(Booking)
admin.site.register(Cinema)
# admin.site.register(Movie)
admin.site.register(Seat)
admin.site.register(Showtime)
admin.site.register(Payment)


class MovieAdmin(admin.ModelAdmin):
    actions = [Movie.update_movies_from_api]


admin.site.register(Movie, MovieAdmin)
