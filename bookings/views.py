from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from events.models import Event
from bookings.models import Booking
from django.http import JsonResponse
import json
import logging
import razorpay
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
# views.py
@login_required


def email_sent_page(request):
    print("=== Email Sent Page View Called ===")
    print(f"User: {request.user}")
    print(f"Session data: {dict(request.session)}")
    return render(request, 'bookings/email.html')


@login_required
def seat_selection(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    logger.info(f"Razorpay Key being used: {settings.RAZORPAY_KEY_ID}")
    context = {
        'event': event,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID
    }
    return render(request, 'bookings/seat_selection.html', context)

@login_required
def get_booked_seats(request, event_id):
    try:
        # Get all booked seats for this event that have completed payment
        booked_seats = Booking.objects.filter(
            event_id=event_id,
            payment_status='COMPLETED'  # Only get seats from completed payments
        ).values_list('seats', flat=True)
        
        # Convert comma-separated seats into a list
        all_booked_seats = []
        for seats in booked_seats:
            all_booked_seats.extend([s.strip() for s in seats.split(',')])
        
        logger.info(f"Retrieved booked seats for event {event_id}: {all_booked_seats}")
        return JsonResponse({'booked_seats': all_booked_seats})
    except Exception as e:
        logger.error(f"Error getting booked seats for event {event_id}: {str(e)}")
        return JsonResponse({'error': 'Error retrieving booked seats'}, status=500)

@login_required
def create_order(request, event_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        # Get selected seats
        data = json.loads(request.body)
        selected_seats = data.get('selected_seats', [])
        logger.info(f"Creating order for seats: {selected_seats}")
        
        # Calculate amount
        amount = len(selected_seats) * settings.SEAT_PRICE * 100  # in paise
        logger.info(f"Calculated amount: {amount} paise (₹{amount/100})")
        
        # First create a booking with PENDING status
        booking = Booking.objects.create(
            user=request.user,
            event_id=event_id,
            seats=','.join(selected_seats),
            amount=amount/100,  # Convert paise to rupees for storing
            payment_status='PENDING',
            booking_email=request.user.email 
        )
        logger.info(f"Created pending booking with ID: {booking.id}")
        
        # Create Razorpay Order
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': f'booking_{booking.id}'  # Use booking ID as receipt
        }
        logger.info(f"Creating Razorpay order with data: {order_data}")
        order = client.order.create(data=order_data)
        logger.info(f"Razorpay order created: {order}")
        
        # Update booking with order ID
        booking.razorpay_order_id = order['id']
        booking.save()
        
        response_data = {
            'order_id': order['id'],
            'amount': amount,
            'user_name': request.user.get_full_name() or request.user.username,
            'user_email': request.user.email
        }
        logger.info(f"Sending response to frontend: {response_data}")
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error in create_order: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def verify_payment(request, event_id):
    print("=== Starting verify_payment ===")
    if request.method != 'POST':
        print("Invalid request method")
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        data = json.loads(request.body)
        print(f"Received data: {data}")
        
        # Get the booking using order ID
        razorpay_order_id = data.get('razorpay_order_id')
        if not razorpay_order_id:
            print("No razorpay_order_id provided")
            return JsonResponse({'error': 'No order ID provided'}, status=400)
            
        booking = get_object_or_404(Booking, razorpay_order_id=razorpay_order_id)
        print(f"Found booking: {booking.id}")
        
        # Verify signature
        params_dict = {
            'razorpay_payment_id': data.get('razorpay_payment_id'),
            'razorpay_order_id': data.get('razorpay_order_id'),
            'razorpay_signature': data.get('razorpay_signature')
        }
        
        try:
            # Verify the payment signature
            print("Verifying payment signature...")
            client.utility.verify_payment_signature(params_dict)
            print("Payment signature verified successfully")
            
            # Update booking status
            booking.payment_status = 'COMPLETED'
            booking.razorpay_payment_id = data['razorpay_payment_id']
            booking.razorpay_signature = data['razorpay_signature']
            booking.save()
            print(f"Booking {booking.id} marked as completed")

            # Send email to the user with the booking details
            print("Starting email sending process...")
            subject = 'YOUR BOOKING HAS BEEN CONFIRMED'
            message = render_to_string('bookings/booking_confirmation_email.html', {
                'booking': booking,
                'event': booking.event,
                'user': booking.user,
                'seats': booking.seats.split(','),
                'amount': booking.amount,
            })
            print("Email template rendered successfully")
            
            try:
                print(f"Attempting to send email to {booking.user.email}")
                print(f"Email settings: HOST={settings.EMAIL_HOST}, PORT={settings.EMAIL_PORT}, USER={settings.EMAIL_HOST_USER}")
                
                send_mail(
                    subject,
                    '',
                    [booking.user.email],
                    html_message=message,
                    fail_silently=False,
                    from_email=settings.EMAIL_HOST_USER,
                )
                print("Email sent successfully")
            except Exception as email_error:
                print(f"Failed to send email: {str(email_error)}")
                print(f"Email error type: {type(email_error)}")
                print(f"Email error details: {email_error.__dict__}")
            
            print("Returning success response")
            return JsonResponse({
                'success': True,
                'redirect_url': '/bookings/email-sent/'
            })
            
        except Exception as e:
            print(f"Payment verification failed: {str(e)}")
            booking.payment_status = 'FAILED'
            booking.save()
            
            return JsonResponse({
                'success': False,
                'error': f'Payment verification failed: {str(e)}'
            }, status=400)
        
    except Exception as e:
        print(f"Error in verify_payment: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    
                            