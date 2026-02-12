from django import forms
from .models import Booking, Match

class BookingForm(forms.Form):
    category = forms.ChoiceField(choices=Booking.CATEGORY_CHOICES, label="Seat Category")
    seats_booked = forms.IntegerField(min_value=1, max_value=10, label="Number of Seats", widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.match = kwargs.pop('match', None)
        super().__init__(*args, **kwargs)

    def clean_seats_booked(self):
        seats = self.cleaned_data['seats_booked']
        category = self.cleaned_data['category']
        available_in_cat = self.match.seats.filter(category=category, is_booked=False).count()
        if available_in_cat < seats:
            raise forms.ValidationError(f"Only {available_in_cat} seats available in {category}!")
        return seats