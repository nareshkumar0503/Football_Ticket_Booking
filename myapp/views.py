from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from .models import Match, Booking, Seat    
from .forms import BookingForm
import requests
import os
import time
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.urls import reverse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from io import BytesIO                           

def homepage(request):
    return render(request, 'myapp/Homepage.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists!')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered!')
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                user.save()
                messages.success(request, 'Account created successfully! Please log in.')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match!')

        return render(request, 'myapp/signup.html')

    return render(request, 'myapp/signup.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = None
        if email and password:
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        if user is not None:
            login(request, user)
            messages.success(request, f"Login successful! Welcome back, {user.username}")
            return redirect('landingpage')           
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'myapp/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('homepage')

@login_required
def landingpage(request):
    matches = Match.objects.filter(match_date__gt=timezone.now()).order_by('match_date')
    return render(request, 'myapp/Landingpage.html', {'matches': matches})

def cart(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Please log in to view your cart.')
        return redirect('login')
    return render(request, 'myapp/cart.html')

@login_required
def book_ticket(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    seats_by_category = {
        'General': match.seats.filter(category='General').order_by('seat_number'),
        'Premium': match.seats.filter(category='Premium').order_by('seat_number'),
        'VIP': match.seats.filter(category='VIP').order_by('seat_number'),
    }
    available_seats = sum(seats.filter(is_booked=False).count() for seats in seats_by_category.values())

    if request.method == 'POST':
        form = BookingForm(request.POST, match=match)
        if form.is_valid():
            selected_seats_str = request.POST.get('selected_seats', '')
            if not selected_seats_str:
                messages.error(request, 'No seats selected!')
            else:
                selected_ids = selected_seats_str.split(',')
                category = form.cleaned_data['category']
                seats = match.seats.filter(id__in=selected_ids, category=category, is_booked=False)
                seats_booked = form.cleaned_data['seats_booked']
                if len(seats) != seats_booked:
                    messages.error(request, 'Invalid seat selection!')
                else:
                    try:
                        with transaction.atomic():
                            price_per_seat = (
                                match.price_general if category == 'General' else
                                match.price_premium if category == 'Premium' else
                                match.price_vip
                            )
                            subtotal = price_per_seat * seats_booked
                            gst = subtotal * 0.18
                            total_price = subtotal + gst

                            for seat in seats:
                                seat.is_booked = True
                                seat.save()

                            booking = Booking.objects.create(
                                user=request.user,
                                match=match,
                                category=category,
                                seats_booked=seats_booked,
                                total_price=total_price
                            )
                            booking.seats.add(*seats)
                            messages.success(request, 'Booking successful! Proceed to payment.')
                            return redirect('payment', booking_id=booking.id)
                    except Exception as e:
                        messages.error(request, f'Booking failed: {str(e)}')
    else:
        form = BookingForm(match=match)

    return render(request, 'myapp/book_ticket.html', {
        'form': form,
        'match': match,
        'seats_by_category': seats_by_category,
        'available_seats': available_seats
    })

@login_required
def payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.payment_status != 'Pending':
        messages.info(request, 'Payment already processed.')
        return redirect('landingpage')

    # ✅ Read from environment variables instead of hardcoding
    app_id = os.getenv("CASHFREE_CLIENT_ID")
    secret = os.getenv("CASHFREE_CLIENT_SECRET")

    if not app_id or not secret:
        messages.error(request, "Payment configuration error. Please contact admin.")
        return redirect('book_ticket', match_id=booking.match.id)

    url = 'https://sandbox.cashfree.com/pg/orders'

    headers = {
        'x-client-id': app_id,
        'x-client-secret': secret,
        'x-api-version': '2023-08-01',
        'Content-Type': 'application/json'
    }

    data = {
        "order_id": f"booking_{booking.id}_{int(time.time())}",
        "order_amount": float(booking.total_price),
        "order_currency": "INR",
        "customer_details": {
            "customer_id": f"user_{booking.user.id}",
            "customer_name": booking.user.username,
            "customer_email": booking.user.email,
            "customer_phone": "9999999999"
        },
        "order_note": f"Booking for {booking.match}",
        "order_meta": {
            "return_url": request.build_absolute_uri(
                reverse('payment_success', args=[booking.id])
            )
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            resp_json = response.json()
            payment_session_id = resp_json.get('payment_session_id')

            if not payment_session_id:
                messages.error(request, 'Failed to get payment session from Cashfree.')
                return redirect('book_ticket', match_id=booking.match.id)

            return render(request, 'myapp/payment.html', {
                'payment_session_id': payment_session_id,
                'booking': booking
            })
        else:
            messages.error(request, f'Cashfree error: {response.text[:200]}')
            return redirect('book_ticket', match_id=booking.match.id)

    except Exception as e:
        messages.error(request, f'Payment request failed: {str(e)}')
        return redirect('book_ticket', match_id=booking.match.id)
    
@login_required
def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.payment_status == 'Pending':
        booking.payment_status = 'Completed'
        booking.save()

    if request.GET.get('force_download'):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        p.setFont("Helvetica-Bold", 24)
        p.drawCentredString(width/2, height - 1.2*inch, "LALIGA e-Ticket")
        p.setFont("Helvetica", 14)
        p.drawCentredString(width/2, height - 1.8*inch, f"Booking #{booking.id}")

        p.setFont("Helvetica-Bold", 16)
        y = height - 3*inch
        p.drawString(1.5*inch, y, f"Match: {booking.match.home_team} vs {booking.match.away_team}")
        y -= 0.5*inch
        p.drawString(1.5*inch, y, f"Date: {booking.match.match_date.strftime('%d %b %Y %H:%M')}")
        y -= 0.4*inch
        p.drawString(1.5*inch, y, f"Venue: {booking.match.stadium}")
        y -= 0.6*inch
        p.drawString(1.5*inch, y, f"Category: {booking.category}")
        y -= 0.4*inch
        p.drawString(1.5*inch, y, f"Seats Booked: {booking.seats_booked}")
        y -= 0.6*inch

        p.setFont("Helvetica-Bold", 18)
        p.drawString(1.5*inch, y, f"Paid: ₹{booking.total_price:.2f}")

        p.setFont("Helvetica", 12)
        p.drawCentredString(width/2, y - 1*inch, "Thank you for booking with LALIGA!")
        p.drawCentredString(width/2, y - 1.3*inch, "Show this ticket at the venue entrance.")

        p.showPage()
        p.save()
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="ticket_{booking.id}.pdf"'
        return response

    return render(request, 'myapp/payment_success.html', {
        'booking': booking
    })

@login_required
def matches(request):
    upcoming_matches = Match.objects.filter(match_date__gt=timezone.now()).order_by('match_date')
    return render(request, 'myapp/matches.html', {'matches': upcoming_matches})

@login_required
def tickets(request):
    user_bookings = Booking.objects.filter(user=request.user).order_by('-booked_on')
    return render(request, 'myapp/tickets.html', {'bookings': user_bookings})