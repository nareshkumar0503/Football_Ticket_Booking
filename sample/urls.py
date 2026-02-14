"""
URL configuration for sample project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# from django.contrib import admin
# from django.urls import path
# from myapp import views

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', views.home, name='home'),
#     path('register/', views.register, name='register'),
#     path('login/', views.user_login, name='login'),
#     path('logout/', views.user_logout, name='logout'),
#     path('book/<int:match_id>/', views.book_ticket, name='book_ticket'),
#     path('history/', views.booking_history, name='booking_history'),
# ]

from django.contrib import admin
from django.urls import path, include
from myapp.admin import admin_site  # ← import this

urlpatterns = [
    path('admin/', admin_site.urls),  # ← use custom admin here
    path('', include('myapp.urls')),
]
