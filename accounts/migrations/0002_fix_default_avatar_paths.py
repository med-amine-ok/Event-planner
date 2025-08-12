from django.db import migrations

def fix_default_avatar_paths(apps, schema_editor):
    Profile = apps.get_model('accounts', 'Profile')
    
    # Update profiles that have the old default path
    profiles_to_update = Profile.objects.filter(avatar='default.jpg')
    for profile in profiles_to_update:
        profile.avatar = 'profile_pics/default.jpg'
        profile.save()

def reverse_fix_default_avatar_paths(apps, schema_editor):
    Profile = apps.get_model('accounts', 'Profile')
    
    # Revert profiles back to old path if needed
    profiles_to_revert = Profile.objects.filter(avatar='profile_pics/default.jpg')
    for profile in profiles_to_revert:
        profile.avatar = 'default.jpg'
        profile.save()

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(fix_default_avatar_paths, reverse_fix_default_avatar_paths),
    ]
