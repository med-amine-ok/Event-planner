#!/usr/bin/env python3
"""
Event Planner Setup Script
Run this script to set up the Event Planner Django application.
"""

import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line

def run_command(command, description):
    """Run a shell command with error handling."""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}:")
        print(f"Error: {e.stderr}")
        return False

def setup_django():
    """Set up Django application."""
    print("\n🚀 Setting up Event Planner Django Application...")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EventPlanner.settings')
    
    try:
        django.setup()
    except Exception as e:
        print(f"❌ Django setup error: {e}")
        return False
    
    return True

def create_migrations():
    """Create and run Django migrations."""
    print("\n📊 Creating database migrations...")
    
    # Create migrations
    print("Creating migrations for accounts app...")
    execute_from_command_line(['manage.py', 'makemigrations', 'accounts'])
    
    print("Creating migrations for events app...")
    execute_from_command_line(['manage.py', 'makemigrations', 'events'])
    
    print("Running migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("✅ Database migrations completed!")

def create_superuser():
    """Optionally create a superuser."""
    response = input("\n🔐 Would you like to create a superuser account? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        print("Creating superuser...")
        execute_from_command_line(['manage.py', 'createsuperuser'])
    else:
        print("Skipping superuser creation.")

def create_sample_data():
    """Create some sample data for testing."""
    print("\n📝 Creating sample data...")
    
    try:
        from django.contrib.auth.models import User
        from events.models import Event
        from datetime import datetime, timedelta
        
        # Create sample user if not exists
        if not User.objects.filter(username='demo').exists():
            demo_user = User.objects.create_user(
                username='demo',
                email='demo@eventplanner.com',
                password='demo123',
                first_name='Demo',
                last_name='User'
            )
            print("✅ Created demo user (username: demo, password: demo123)")
        
        # Create sample events
        if Event.objects.count() == 0:
            sample_events = [
                {
                    'title': 'Welcome to Event Planner',
                    'description': 'Join us for an introduction to our amazing event planning platform! Learn how to create events, manage RSVPs, and connect with your community.',
                    'location': 'Community Center, Main St 123',
                    'date': datetime.now().date() + timedelta(days=7),
                    'time': datetime.now().time().replace(hour=18, minute=0),
                    'capacity': 50,
                    'creator': User.objects.first()
                },
                {
                    'title': 'Monthly Networking Meetup',
                    'description': 'Connect with local professionals and entrepreneurs. Great opportunity to expand your network and share ideas.',
                    'location': 'Downtown Business Hub',
                    'date': datetime.now().date() + timedelta(days=14),
                    'time': datetime.now().time().replace(hour=19, minute=30),
                    'capacity': 30,
                    'creator': User.objects.first()
                },
                {
                    'title': 'Weekend Workshop: Web Development',
                    'description': 'Learn the basics of web development in this hands-on workshop. Suitable for beginners!',
                    'location': 'Tech Campus, Room 201',
                    'date': datetime.now().date() + timedelta(days=21),
                    'time': datetime.now().time().replace(hour=10, minute=0),
                    'capacity': 25,
                    'creator': User.objects.first()
                }
            ]
            
            for event_data in sample_events:
                Event.objects.create(**event_data)
            
            print(f"✅ Created {len(sample_events)} sample events")
        
    except Exception as e:
        print(f"⚠️ Could not create sample data: {e}")

def main():
    """Main setup function."""
    print("=" * 60)
    print("🎉 EVENT PLANNER SETUP")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Error: manage.py not found. Please run this script from the EventPlanner directory.")
        sys.exit(1)
    
    # Setup Django
    if not setup_django():
        print("❌ Failed to setup Django. Exiting.")
        sys.exit(1)
    
    # Create and run migrations
    try:
        create_migrations()
    except Exception as e:
        print(f"❌ Migration error: {e}")
        sys.exit(1)
    
    # Create superuser
    create_superuser()
    
    # Create sample data
    create_sample_data()
    
    # Create media directories
    media_dirs = ['media', 'media/profile_pics', 'media/event_pics']
    for directory in media_dirs:
        os.makedirs(directory, exist_ok=True)
    print("✅ Created media directories")
    
    # Final instructions
    print("\n" + "=" * 60)
    print("🎊 SETUP COMPLETE!")
    print("=" * 60)
    print("\n📋 Next Steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Start the server: python manage.py runserver")
    print("3. Open your browser to: http://127.0.0.1:8000")
    print("4. Admin panel: http://127.0.0.1:8000/admin")
    
    try:
        from django.contrib.auth.models import User
        if User.objects.filter(username='demo').exists():
            print("\n🔑 Demo Account:")
            print("   Username: demo")
            print("   Password: demo123")
    except ImportError:
        pass
    
    print("\n📚 Documentation: README.md")
    print("💡 For help: Check the README.md file")
    print("\n🚀 Happy Event Planning!")

if __name__ == '__main__':
    main()
