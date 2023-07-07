from django import forms
from .models import Booking, Cinema, Movie, Seat


class BookingForm(forms.ModelForm):
    row = forms.IntegerField()
    number = forms.IntegerField()
    movie = forms.ModelChoiceField(queryset=Movie.objects.all())
    cinema = forms.ModelChoiceField(queryset=Cinema.objects.all())

    class Meta:
        model = Booking
        fields = ["row", "number", "movie", "cinema"]

    def clean(self):
        cleaned_data = super().clean()
        row = cleaned_data.get("row")
        number = cleaned_data.get("number")
        cinema = cleaned_data.get("cinema")

        if row and number and cinema:
            # Get or create the seat based on the row and number
            seat, created = Seat.objects.get_or_create(row=row, number=number)
            if seat.is_booked:
                raise forms.ValidationError(
                    "Invalid seat selection. Please select a valid seat."
                )
            cleaned_data["seat"] = seat

        return cleaned_data
