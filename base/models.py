from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=200)
    director = models.CharField(max_length=200)
    duration = models.CharField(max_length=50)
    rating = models.FloatField()

    def __str__(self):
        return self.title


class Seat(models.Model):
    row = models.IntegerField()
    number = models.IntegerField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.row},{self.number}, {self.is_booked}"


class Booking(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.movie},{self.seat}"


class Cinema(models.Model):
    name = models.CharField(max_length=200)
    rows = models.IntegerField()
    seats_per_row = models.IntegerField()
    movies = models.ManyToManyField(Movie)
    seats = models.ManyToManyField(Seat)

    def __str__(self):
        return self.name
