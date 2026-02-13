from django.contrib import admin
from django.utils.html import format_html
from .models import Team, Stadium, Match, Booking, Seat


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_preview', 'logo_url')
    search_fields = ('name',)
    readonly_fields = ('logo_preview',)

    def logo_preview(self, obj):
        if obj.logo_url:
            return format_html(
                '<img src="{}" style="max-height: 60px; border-radius: 6px;" />',
                obj.logo_url
            )
        return "No logo"
    logo_preview.short_description = "Logo"


@admin.register(Stadium)
class StadiumAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name', 'location')


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'away_team', 'stadium', 'match_date', 'is_upcoming')
    list_filter = ('stadium', 'match_date')
    search_fields = ('home_team__name', 'away_team__name')
    date_hierarchy = 'match_date'
    list_per_page = 20

    def is_upcoming(self, obj):
        from django.utils import timezone
        return format_html(
            '<span style="color: {};">{}</span>',
            'limegreen' if obj.match_date > timezone.now() else 'tomato',
            "Upcoming" if obj.match_date > timezone.now() else "Past"
        )
    is_upcoming.short_description = "Status"
    is_upcoming.boolean = False  # shows colored text instead of check


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'user_link', 'match', 'category', 'seats_booked',
        'total_price_display', 'booked_on', 'payment_status_colored'
    )
    list_filter = ('category', 'payment_status', 'booked_on')
    search_fields = ('user__username', 'match__home_team__name', 'match__away_team__name')
    date_hierarchy = 'booked_on'
    list_per_page = 25

    def user_link(self, obj):
        return format_html(
            '<a href="/admin/auth/user/{}/change/">{}</a>',
            obj.user.id, obj.user.username
        )
    user_link.short_description = "User"

    def total_price_display(self, obj):
        return f"₹{obj.total_price:,.2f}" if obj.total_price else "—"
    total_price_display.short_description = "Total"

    def payment_status_colored(self, obj):
        colors = {
            'paid': 'limegreen',
            'pending': 'orange',
            'failed': 'tomato',
            'refunded': 'gray',
        }
        color = colors.get(obj.payment_status.lower(), 'gray')
        return format_html(
            '<span style="color: {}; font-weight: 600;">{}</span>',
            color, obj.payment_status.upper()
        )
    payment_status_colored.short_description = "Payment"


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('match', 'category', 'seat_number', 'status_badge')
    list_filter = ('category', 'is_booked', 'match')
    search_fields = ('seat_number', 'match__home_team__name')
    list_per_page = 50

    def status_badge(self, obj):
        if obj.is_booked:
            return format_html(
                '<span style="background:#ef4444; color:white; padding:4px 10px; border-radius:12px; font-weight:bold;">BOOKED</span>'
            )
        return format_html(
            '<span style="background:#22c55e; color:white; padding:4px 10px; border-radius:12px; font-weight:bold;">AVAILABLE</span>'
        )
    status_badge.short_description = "Status"