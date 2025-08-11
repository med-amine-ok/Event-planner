from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta, date as date_cls
import json

from .models import Event, RSVP, Rating
from .forms import EventForm, RSVPForm, RatingForm, EventSearchForm


class EventListView(ListView):
    model = Event
    template_name = 'events/home.html'
    context_object_name = 'events'
    paginate_by = 6
    
    def get_queryset(self):
        # Show all events created by users instead of filtering by end time
        queryset = Event.objects.all()
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(location__icontains=search_query)
            )
        
        # Location filter
        location_filter = self.request.GET.get('location')
        if location_filter:
            queryset = queryset.filter(location__icontains=location_filter)
        
        # Date range filter
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        # Avoid clashing with Event.attendee_count @property by using a different annotation name
        queryset = queryset.annotate(going_count=Count('rsvps', filter=Q(rsvps__status='going')))
        # Order events by scheduled date and time
        return queryset.order_by('date', 'time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = EventSearchForm(self.request.GET)
        context['total_events'] = Event.objects.count()  # Count all events, not just upcoming
        return context


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        
        # Check if user has RSVP'd
        user_rsvp = None
        if self.request.user.is_authenticated:
            try:
                user_rsvp = RSVP.objects.get(event=event, user=self.request.user)
            except RSVP.DoesNotExist:
                pass
        
        context['user_rsvp'] = user_rsvp
        context['rsvp_form'] = RSVPForm()
        context['attendees'] = event.rsvps.filter(status='going').select_related('user')
        
        # Calculate time until event
        if not event.is_past:
            event_datetime = datetime.combine(event.date, event.time)
            now = datetime.now()
            if event_datetime > now:
                time_diff = event_datetime - now
                context['time_until_event'] = {
                    'days': time_diff.days,
                    'hours': time_diff.seconds // 3600,
                    'minutes': (time_diff.seconds % 3600) // 60
                }
            # Expose expected end for UI
            if event.end_datetime:
                context['end_datetime'] = event.end_datetime
        
        # Add capacity percentage calculation
        if event.capacity:
            capacity_percentage = (event.attendee_count / event.capacity) * 100
            context['capacity_percentage'] = min(capacity_percentage, 100)  # Cap at 100%
        
        return context


class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    
    def form_valid(self, form):
        form.instance.creator = self.request.user
        messages.success(self.request, 'Event created successfully!')
        return super().form_valid(form)


class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Event updated successfully!')
        return super().form_valid(form)
    
    def test_func(self):
        event = self.get_object()
        return self.request.user == event.creator


class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = '/'
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Event deleted successfully!')
        return super().delete(request, *args, **kwargs)
    
    def test_func(self):
        event = self.get_object()
        return self.request.user == event.creator


@login_required
def rsvp_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    # Prevent RSVP updates for completed events or past events
    if event.is_completed:
        messages.error(request, 'Cannot update attendance for completed events.')
        return redirect('event-detail', pk=pk)
    
    if event.is_past:
        messages.error(request, 'Cannot attend past events.')
        return redirect('event-detail', pk=pk)
    
    if request.method == 'POST':
        form = RSVPForm(request.POST)
        if form.is_valid():
            rsvp, created = RSVP.objects.get_or_create(
                event=event,
                user=request.user,
                defaults={'status': form.cleaned_data['status']}
            )
            
            if not created:
                rsvp.status = form.cleaned_data['status']
                rsvp.save()
            
            status_text = 'going' if form.cleaned_data['status'] == 'going' else 'not going'
            messages.success(request, f'RSVP updated! You are {status_text} to this event.')
        else:
            messages.error(request, 'There was an error with your RSVP.')
    
    return redirect('event-detail', pk=pk)


@login_required
def rate_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    if not event.is_past:
        messages.error(request, 'You can only rate events that have already happened.')
        return redirect('event-detail', pk=pk)
    
    # Check if user actually attended the event (RSVP'd as 'going')
    try:
        user_rsvp = RSVP.objects.get(event=event, user=request.user)
        if user_rsvp.status != 'going':
            messages.error(request, 'You can only rate events that you actually attended.')
            return redirect('event-detail', pk=pk)
    except RSVP.DoesNotExist:
        messages.error(request, 'You can only rate events that you actually attended.')
        return redirect('event-detail', pk=pk)
    
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating, created = Rating.objects.get_or_create(
                event=event,
                user=request.user,
                defaults={
                    'stars': form.cleaned_data['stars'],
                    'feedback': form.cleaned_data['feedback']
                }
            )
            if not created:
                # Update existing rating
                rating.stars = form.cleaned_data['stars']
                rating.feedback = form.cleaned_data['feedback']
                rating.save()
                messages.success(request, 'Your rating has been updated!')
            else:
                messages.success(request, 'Thank you for rating this event!')
            
            # Redirect back to the page they came from
            referer = request.META.get('HTTP_REFERER')
            if referer:
                return redirect(referer)
            return redirect('event-detail', pk=pk)
    else:
        form = RatingForm()
    
    return render(request, 'events/rate_event.html', {
        'event': event,
        'form': form
    })


@login_required
def mark_event_completed(request, pk):
    """Mark an event as completed. Only accessible to event creator."""
    event = get_object_or_404(Event, pk=pk)
    
    # Check if user is the event creator
    if request.user != event.creator:
        messages.error(request, 'Only the event creator can mark events as completed.')
        return redirect('event-detail', pk=pk)
    
    # Mark event as completed
    event.is_completed = True
    event.save()
    
    messages.success(request, f'Event "{event.title}" has been marked as completed!')
    
    # Redirect back to the event detail page
    return redirect('event-detail', pk=pk)


@login_required
def undo_event_completed(request, pk):
    """Undo marking an event as completed. Only accessible to event creator."""
    event = get_object_or_404(Event, pk=pk)
    
    # Check if user is the event creator
    if request.user != event.creator:
        messages.error(request, 'Only the event creator can undo marking events as completed.')
        return redirect('event-detail', pk=pk)
    
    # Check if event is actually completed
    if not event.is_completed:
        messages.warning(request, f'Event "{event.title}" is not marked as completed.')
        return redirect('event-detail', pk=pk)
    
    # Undo the completed status
    event.is_completed = False
    event.save()
    
    messages.success(request, f'Event "{event.title}" is no longer marked as completed!')
    
    # Redirect back to the event detail page
    return redirect('event-detail', pk=pk)


class CompletedEventsView(ListView):
    model = Event
    template_name = 'events/completed_events.html'
    context_object_name = 'events'
    paginate_by = 6
    
    def get_queryset(self):
        # Avoid clashing with Event.attendee_count @property by using a different annotation name
        queryset = Event.objects.filter(
            Q(is_completed=True) | Q(end_datetime__lt=timezone.now())
        ).annotate(going_count=Count('rsvps', filter=Q(rsvps__status='going')))
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(location__icontains=search_query)
            )
        
        return queryset.order_by('-date', '-time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = EventSearchForm(self.request.GET)
        
        if self.request.user.is_authenticated:
            for event in context['events']:
                # Check if user can rate (event is past, user hasn't rated yet, AND user attended the event)
                try:
                    user_rating = Rating.objects.get(event=event, user=self.request.user)
                    event.can_rate = False  # User already rated
                    event.user_rating = user_rating
                except Rating.DoesNotExist:
                    # Check if user actually attended the event
                    try:
                        user_rsvp = RSVP.objects.get(event=event, user=self.request.user)
                        if user_rsvp.status == 'going':
                            event.can_rate = True  # User can rate (event is past and user attended)
                        else:
                            event.can_rate = False  # User didn't attend
                    except RSVP.DoesNotExist:
                        event.can_rate = False  # User never RSVP'd
        
        context['rating_form'] = RatingForm()
        return context


@login_required
def my_rsvps(request):
    upcoming_rsvps = RSVP.objects.filter(
        user=request.user,
        event__date__gte=timezone.now().date()
    ).select_related('event').order_by('event__date', 'event__time')
    
    past_rsvps = RSVP.objects.filter(
        user=request.user,
        event__date__lt=timezone.now().date()
    ).select_related('event').order_by('-event__date', '-event__time')
    
    # Add rating context for past events
    for rsvp in past_rsvps:
        try:
            user_rating = Rating.objects.get(event=rsvp.event, user=request.user)
            rsvp.event.can_rate = False  # User already rated
            rsvp.event.user_rating = user_rating
        except Rating.DoesNotExist:
            # Only allow rating if user actually attended the event
            if rsvp.status == 'going':
                rsvp.event.can_rate = True  # User can rate (event is past and user attended)
            else:
                rsvp.event.can_rate = False  # User didn't attend
    
    return render(request, 'events/my_rsvps.html', {
        'upcoming_rsvps': upcoming_rsvps,
        'past_rsvps': past_rsvps,
        'rating_form': RatingForm()
    })


def calendar_events_api(request):
    """API endpoint for calendar view. Shows all events created by users."""
    # Show all events instead of filtering by date range
    events_qs = Event.objects.all().order_by('date', 'time')

    events_data = []
    for event in events_qs:
        events_data.append({
            'id': event.id,
            'title': event.title,
            'start': f"{event.date}T{event.time}",
            'url': reverse('event-detail', args=[event.id]),
            'backgroundColor': '#FF7F50',
            'borderColor': '#FF8C42',
            'textColor': '#ffffff'
        })

    return JsonResponse(events_data, safe=False)
