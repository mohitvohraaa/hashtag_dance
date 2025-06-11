from django.urls import path, include
from . import views

app_name = 'bookings'

urlpatterns = [
    path('event/<int:event_id>/select/', views.seat_selection, name='seat_selection'),
    path('api/event/<int:event_id>/booked-seats/', views.get_booked_seats, name='get_booked_seats'),
   # path('get_locked_seats/<int:event_id>/', views.get_locked_seats, name='get_locked_seats'),
    path('api/event/<int:event_id>/release-locked-seats/', views.release_locked_seats, name='release_locked_seats'),

    path('api/event/<int:event_id>/create-order/', views.create_order, name='create_order'),
    path('api/event/<int:event_id>/verify-payment/', views.verify_payment, name='verify_payment'),
    path('email-sent/', views.email_sent_page, name='email_sent_page')
]
