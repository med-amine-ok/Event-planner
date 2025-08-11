from django.contrib import admin
from .models import Event, RSVP, Rating, ReminderLog


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'time', 'location', 'creator', 'attendee_count']
    list_filter = ['date', 'creator']
    search_fields = ['title', 'location', 'description']
    date_hierarchy = 'date'


@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'event__title']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'stars', 'created_at']
    list_filter = ['stars', 'created_at']
    search_fields = ['user__username', 'event__title']


@admin.register(ReminderLog)
class ReminderLogAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'reminder_type', 'sent_at']
    list_filter = ['reminder_type', 'sent_at']
    search_fields = ['event__title', 'user__username']
