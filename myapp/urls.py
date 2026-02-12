from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('landing/', views.landingpage, name='landingpage'),
    path('cart/', views.cart, name='cart'),
    path('logout/', views.logout_view, name='logout'),
    path('book/<int:match_id>/', views.book_ticket, name='book_ticket'),
    path('payment/<int:booking_id>/', views.payment, name='payment'),
    path('payment-success/<int:booking_id>/', views.payment_success, name='payment_success'),
    path('matches/', views.matches, name='matches'),
    path('tickets/', views.tickets, name='tickets'),
]   