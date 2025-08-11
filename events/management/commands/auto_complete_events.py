from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Event


class Command(BaseCommand):
    help = 'Automatically mark events as completed based on their auto_complete_datetime'

    def handle(self, *args, **options):
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
            self.stdout.write(
                self.style.SUCCESS(
                    f'Event "{event.title}" (ID: {event.pk}) marked as completed automatically'
                )
            )
        
        if completed_count == 0:
            self.stdout.write(
                self.style.WARNING('No events were auto-completed')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully auto-completed {completed_count} event(s)'
                )
            )
