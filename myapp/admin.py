from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.template.response import TemplateResponse
from django.utils.html import format_html
from django.utils import timezone
from .models import Team, Stadium, Match, Booking, Seat
from django.db.models import Sum, Count

class CustomAdminSite(AdminSite):
    site_header = "La Liga Admin Panel ⚽"
    site_title = "La Liga Admin"
    index_template = 'admin/custom_index.html'  # our new template

    def index(self, request, extra_context=None):
        # Calculate stats
        total_matches = Match.objects.count()
        upcoming_matches = Match.objects.filter(match_date__gt=timezone.now()).count()
        total_bookings = Booking.objects.count()
        total_revenue = Booking.objects.filter(payment_status='Completed').aggregate(Sum('total_price'))['total_price__sum'] or 0
        total_seats = Match.objects.aggregate(Sum('total_seats'))['total_seats__sum'] or 0
        booked_seats = Booking.objects.aggregate(Sum('seats_booked'))['seats_booked__sum'] or 0
        seat_occupancy = round((booked_seats / total_seats * 100), 1) if total_seats > 0 else 0

        recent_bookings = Booking.objects.order_by('-booked_on')[:5]

        extra_context = extra_context or {}
        extra_context.update({
            'total_matches': total_matches,
            'upcoming_matches': upcoming_matches,
            'total_bookings': total_bookings,
            'total_revenue': total_revenue,
            'seat_occupancy': seat_occupancy,
            'recent_bookings': recent_bookings,
        })
        return super().index(request, extra_context)

admin_site = CustomAdminSite(name='custom_admin')

# Register models with custom site
admin_site.register(Team)
admin_site.register(Stadium)
admin_site.register(Match)
admin_site.register(Booking)
admin_site.register(Seat)