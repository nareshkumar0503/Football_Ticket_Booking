from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Team(models.Model):
    name = models.CharField(max_length=100)
    logo_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class Stadium(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class Match(models.Model):
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE)
    match_date = models.DateTimeField()
    price_general = models.IntegerField(default=500)
    price_premium = models.IntegerField(default=1000)
    price_vip = models.IntegerField(default=2000)
    total_seats = models.IntegerField(default=50000)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} on {self.match_date.date()}"

class Seat(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='seats')
    category = models.CharField(max_length=20, choices=[('General', 'General'), ('Premium', 'Premium'), ('VIP', 'VIP')])
    seat_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.category} {self.seat_number} for {self.match}"

@receiver(post_save, sender=Match)
def create_seats(sender, instance, created, **kwargs):
    if created:
        for category in ['General', 'Premium', 'VIP']:
            for i in range(1, 21):
                Seat.objects.create(match=instance, category=category, seat_number=f"{category[0]}{i}")

class Booking(models.Model):
    CATEGORY_CHOICES = [('General', 'General'), ('Premium', 'Premium'), ('VIP', 'VIP')]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    seats_booked = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    booked_on = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, default='Pending', choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Failed', 'Failed')])
    seats = models.ManyToManyField(Seat)

    def __str__(self):
        return f"{self.user.username} - {self.match} ({self.seats_booked} seats)"