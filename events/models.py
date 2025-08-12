from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from PIL import Image
import os
from datetime import datetime, timedelta


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=300)
    duration_days = models.PositiveIntegerField(default=0, help_text="Duration in days")
    duration_hours = models.PositiveIntegerField(default=0, help_text="Duration in hours")
    auto_complete_days = models.PositiveIntegerField(default=0, help_text="Days after event start to auto-complete")
    auto_complete_hours = models.PositiveIntegerField(default=0, help_text="Hours after event start to auto-complete")
    capacity = models.PositiveIntegerField(blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    image = models.ImageField(default='event_pics/event_default.png', upload_to='event_pics')
    end_datetime = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False, help_text="Mark this event as manually completed")
    auto_complete_datetime = models.DateTimeField(blank=True, null=True, help_text="Event will be automatically marked as completed at this date and time")
    
    class Meta:
        ordering = ['date', 'time']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('event-detail', kwargs={'pk': self.pk})
    
    @property
    def is_past(self):
        # Consider the event completed when current time passes end_datetime
        if self.end_datetime:
            return timezone.now() > self.end_datetime
        # Fallback to date-only comparison if end not set
        return timezone.now().date() > self.date
    
    @property
    def can_be_marked_completed(self):
        # Event can be marked as completed if it's past or if creator manually marks it
        return self.is_past or self.is_completed
    
    @property
    def attendee_count(self):
        return self.rsvps.filter(status='going').count()
    
    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return sum(rating.stars for rating in ratings) / len(ratings)
        return 0
    
    def save(self, *args, **kwargs):
        # Compute end_datetime from date, time, and duration
        try:
            start_naive = datetime.combine(self.date, self.time)
            tz = timezone.get_current_timezone()
            start_dt = timezone.make_aware(start_naive, tz) if timezone.is_naive(start_naive) else start_naive
            
            # Calculate duration from days and hours
            duration = timedelta(days=self.duration_days or 0, hours=self.duration_hours or 0)
            self.end_datetime = start_dt + duration
            
            # Calculate auto_complete_datetime based on days and hours
            if self.auto_complete_days or self.auto_complete_hours:
                auto_complete_delta = timedelta(days=self.auto_complete_days or 0, hours=self.auto_complete_hours or 0)
                self.auto_complete_datetime = start_dt + auto_complete_delta
        except Exception:
            # If any field missing during creation form clean, skip computation
            pass

        super().save(*args, **kwargs)

        # Resize image only when stored on local filesystem (e.g., dev or non-cloud storage)
        image_path = getattr(self.image, 'path', None)
        if Image and self.image and image_path and os.path.isfile(image_path):
            try:
                img = Image.open(image_path)
                if img.height > 800 or img.width > 800:
                    output_size = (800, 800)
                    img.thumbnail(output_size)
                    img.save(image_path)
            except Exception:
                pass


class RSVP(models.Model):
    STATUS_CHOICES = [
        ('going', 'Going'),
        ('not_going', 'Not Going'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['event', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.event.title} - {self.status}"


class Rating(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stars = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['event', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.event.title} - {self.stars} stars"


class ReminderLog(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reminder_type = models.CharField(max_length=20, choices=[
        ('pre_event', 'Pre Event'),
        ('post_event', 'Post Event Rating'),
    ])
    sent_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.reminder_type} - {self.event.title} - {self.user.username}"
