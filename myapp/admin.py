from django.contrib import admin
from .models import Team, Stadium, Match, Booking, Seat  

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_url')
    search_fields = ('name',)

@admin.register(Stadium)
class StadiumAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name', 'location')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'away_team', 'stadium', 'match_date')
    list_filter = ('stadium', 'match_date')
    search_fields = ('home_team__name', 'away_team__name')
    date_hierarchy = 'match_date'  

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'match', 'category', 'seats_booked', 'total_price', 'booked_on', 'payment_status')
    list_filter = ('category', 'payment_status', 'booked_on')
    search_fields = ('user__username', 'match__home_team__name')
    date_hierarchy = 'booked_on'

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('match', 'category', 'seat_number', 'is_booked')
    list_filter = ('category', 'is_booked')
    search_fields = ('seat_number',)