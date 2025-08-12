from django.db import migrations

def fix_default_event_image_paths(apps, schema_editor):
    Event = apps.get_model('events', 'Event')
    
    # Update events that have the old default path
    events_to_update = Event.objects.filter(image='event_default.jpg')
    for event in events_to_update:
        event.image = 'event_pics/event_default.png'
        event.save()

def reverse_fix_default_event_image_paths(apps, schema_editor):
    Event = apps.get_model('events', 'Event')
    
    # Revert events back to old path if needed
    events_to_revert = Event.objects.filter(image='event_pics/event_default.png')
    for event in events_to_revert:
        event.image = 'event_default.jpg'
        event.save()

class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_remove_event_duration_minutes_event_duration_days_and_more'),
    ]

    operations = [
        migrations.RunPython(fix_default_event_image_paths, reverse_fix_default_event_image_paths),
    ]
