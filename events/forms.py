from django import forms
from django.utils import timezone
from .models import Event, RSVP, Rating


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'time', 'location', 'capacity', 'image', 'auto_complete_days', 'auto_complete_hours']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date()}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'title': forms.TextInput(attrs={'placeholder': 'Enter event title'}),
            'location': forms.TextInput(attrs={'placeholder': 'Enter event location'}),
            'capacity': forms.NumberInput(attrs={'placeholder': 'Maximum attendees (optional)', 'min': 1}),
            'auto_complete_days': forms.NumberInput(attrs={
                'min': 0, 'step': 1, 'placeholder': 'Days after event start (optional)',
                'class': 'form-control'
            }),
            'auto_complete_hours': forms.NumberInput(attrs={
                'min': 0, 'step': 1, 'placeholder': 'Hours after event start (optional)',
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class RSVPForm(forms.ModelForm):
    class Meta:
        model = RSVP
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'})
        }


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['stars', 'feedback']
        widgets = {
            'stars': forms.Select(choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)], 
                                attrs={'class': 'form-select'}),
            'feedback': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 
                                            'placeholder': 'Share your experience (optional)'}),
        }


class EventSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search events...',
            'class': 'form-control'
        })
    )
    location = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Filter by location...',
            'class': 'form-control'
        })
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
