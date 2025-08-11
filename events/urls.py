from django.urls import path
from .views import (
    EventListView, EventDetailView, EventCreateView, 
    EventUpdateView, EventDeleteView, CompletedEventsView,
    rsvp_event, rate_event, mark_event_completed, undo_event_completed, my_rsvps, calendar_events_api
)

urlpatterns = [
    path('', EventListView.as_view(), name='events-home'),
    path('event/<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('event/new/', EventCreateView.as_view(), name='event-create'),
    path('event/<int:pk>/update/', EventUpdateView.as_view(), name='event-update'),
    path('event/<int:pk>/delete/', EventDeleteView.as_view(), name='event-delete'),
    path('event/<int:pk>/rsvp/', rsvp_event, name='event-rsvp'),
    path('event/<int:pk>/rate/', rate_event, name='event-rate'),
    path('event/<int:pk>/complete/', mark_event_completed, name='event-complete'),
    path('event/<int:pk>/undo-complete/', undo_event_completed, name='event-undo-complete'),
    path('completed/', CompletedEventsView.as_view(), name='completed-events'),
    path('my-rsvps/', my_rsvps, name='my-rsvps'),
    path('api/calendar-events/', calendar_events_api, name='calendar-events-api'),
]
