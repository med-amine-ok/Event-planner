from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from .models import Event, RSVP, ReminderLog, Rating


def send_event_reminders():
    """Send email reminders 2 days before events"""
    # Get events happening in 2 days
    reminder_date = timezone.now().date() + timedelta(days=2)
    events = Event.objects.filter(date=reminder_date)
    
    for event in events:
        # Get all users who RSVP'd as going
        attendees = RSVP.objects.filter(event=event, status='going').select_related('user')
        
        for rsvp in attendees:
            user = rsvp.user
            
            # Check if reminder already sent
            if not ReminderLog.objects.filter(
                event=event, 
                user=user, 
                reminder_type='pre_event'
            ).exists():
                
                # Send email
                subject = f'Reminder: {event.title} is in 2 days!'
                message = f"""
                Hi {user.first_name or user.username},

                This is a friendly reminder that you have RSVP'd to attend:

                Event: {event.title}
                Date: {event.date.strftime('%B %d, %Y')}
                Time: {event.time.strftime('%I:%M %p')}
                Location: {event.location}

                We're looking forward to seeing you there!

                Best regards,
                Event Planner Team
                """
                
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@eventplanner.com',
                        [user.email],
                        fail_silently=False,
                    )
                    
                    # Log that reminder was sent
                    ReminderLog.objects.create(
                        event=event,
                        user=user,
                        reminder_type='pre_event'
                    )
                    print(f"Reminder sent to {user.email} for event: {event.title}")
                    
                except Exception as e:
                    print(f"Failed to send reminder to {user.email}: {str(e)}")


def auto_complete_events():
    """Automatically mark events as completed based on auto_complete_datetime"""
    now = timezone.now()
    
    # Find events that should be auto-completed
    events_to_complete = Event.objects.filter(
        auto_complete_datetime__lte=now,
        is_completed=False
    )
    
    completed_count = 0
    
    for event in events_to_complete:
        event.is_completed = True
        event.save()
        completed_count += 1
        print(f"Event '{event.title}' (ID: {event.pk}) marked as completed automatically")
    
    if completed_count > 0:
        print(f"Successfully auto-completed {completed_count} event(s)")
    else:
        print("No events were auto-completed")


def send_rating_requests():
    """Send rating request emails after events end"""
    # Get events that ended yesterday
    yesterday = timezone.now().date() - timedelta(days=1)
    events = Event.objects.filter(date=yesterday)
    
    for event in events:
        # Get all users who attended (RSVP'd as going)
        attendees = RSVP.objects.filter(event=event, status='going').select_related('user')
        
        for rsvp in attendees:
            user = rsvp.user
            
            # Check if rating request already sent
            if not ReminderLog.objects.filter(
                event=event, 
                user=user, 
                reminder_type='post_event'
            ).exists():
                
                # Check if user hasn't already rated
                if not Rating.objects.filter(event=event, user=user).exists():
                    
                    # Send email
                    subject = f'How was {event.title}? Please rate your experience!'
                    message = f"""
                    Hi {user.first_name or user.username},

                    Thank you for attending {event.title} yesterday!

                    We hope you had a great time. Please take a moment to rate your experience and help other users discover great events.

                    You can rate the event by visiting: http://localhost:8000/event/{event.id}/

                    Your feedback is valuable to us and helps event organizers improve future events.

                    Best regards,
                    Event Planner Team
                    """
                    
                    try:
                        send_mail(
                            subject,
                            message,
                            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@eventplanner.com',
                            [user.email],
                            fail_silently=False,
                        )
                        
                        # Log that rating request was sent
                        ReminderLog.objects.create(
                            event=event,
                            user=user,
                            reminder_type='post_event'
                        )
                        print(f"Rating request sent to {user.email} for event: {event.title}")
                        
                    except Exception as e:
                        print(f"Failed to send rating request to {user.email}: {str(e)}")


def test_send_reminder():
    """Test function to manually trigger reminder sending"""
    print("Testing reminder system...")
    send_event_reminders()
    send_rating_requests()
    print("Test completed!")
