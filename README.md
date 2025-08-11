# Event Planner - Django Web Application

A modern, responsive event planning and management system built with Django and Bootstrap 5.

## Features

### 🎯 Core Features
- **User Authentication**: Registration, login/logout, password reset, and user profiles
- **Event Management**: Create, edit, delete events with images, dates, locations, and capacity
- **RSVP System**: Users can RSVP "Going" or "Not Going" to events
- **Event Duration & Auto-Completion**: Configure duration in days/hours; end time is auto-calculated. Optionally set an auto-complete time to mark events completed automatically.
- **Manual Completion Controls**: Event creators can mark events as completed or undo completion.
- **Event Reminders**: Automated email notifications 2 days before events; post-event rating requests 1 day after
- **Rating System**: Post-event rating and feedback system (only for attendees)
- **Calendar View**: Monthly/weekly calendar display using FullCalendar.js
- **Search & Filter**: Advanced event search by title, location, and date range

### 🎨 Modern UI/UX
- **Orange Color Scheme**: Professional orange gradient theme (#FF7F50, #FF8C42, #FFB347, #FFE5B4)
- **Responsive Design**: Mobile-first Bootstrap 5 implementation
- **Sidebar Navigation**: Clean sidebar with user info and main navigation
- **Interactive Elements**: Hover effects, animations, and smooth transitions
- **Card-based Layout**: Modern card designs for events and content

### 📱 Pages & Functionality
- **Dashboard**: Welcome section, event search, events grid, calendar view
- **Event Details**: Comprehensive event information, RSVP controls, attendee lists, capacity indicator, ratings
- **Event Creation**: Multi-step form with validation and image upload
- **Profile Management**: User profiles with avatar upload and activity stats
- **My RSVPs**: Track upcoming and past event attendance with quick rating access
- **Completed Events**: Archive of past/auto-completed events with rating capability

## Installation & Setup

### Prerequisites
- Python 3.10+ (tested with Python 3.12)
- pip
- Virtual environment (recommended)

### Installation Steps

1. **Clone/Extract the project**
   ```bash
   cd Event_planner/EventPlanner
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # OR using Pipenv
   pipenv install
   pipenv shell
   ```

4. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Collect static files (if needed)**
   ```bash
   python manage.py collectstatic
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Open your browser to `http://127.0.0.1:8000`
   - Admin panel: `http://127.0.0.1:8000/admin`

## Project Structure

```
EventPlanner/
├── EventPlanner/           # Main project settings
│   ├── settings.py         # Django settings
│   ├── urls.py            # Main URL configuration
│   └── ...
├── accounts/              # User authentication app
│   ├── models.py          # User profile model
│   ├── views.py           # Auth views
│   ├── forms.py           # User forms
│   └── ...
├── events/                # Events management app
│   ├── models.py          # Event, RSVP, Rating models
│   ├── views.py           # Event views
│   ├── forms.py           # Event forms
│   ├── admin.py           # Admin configuration
│   └── cron.py            # Email reminder system
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── events/            # Event templates
│   └── accounts/          # Account templates
├── static/                # Static files
│   ├── css/main.css       # Main stylesheet
│   └── js/main.js         # JavaScript functionality
├── media/                 # User uploaded files
└── manage.py              # Django management script
```

## Database Models

### User Profile
- Extended Django User model
- Avatar image upload
- Bio, location, birth date

### Event
- Title, description, location
- Date, time, capacity
- Duration: `duration_days`, `duration_hours`
- Calculated fields: `end_datetime`
- Completion: `is_completed`, optional `auto_complete_days`, `auto_complete_hours`, and computed `auto_complete_datetime`
- Creator (foreign key to User)
- Image upload
- Timestamps

### RSVP
- Event and User relationship
- Status: "going" or "not_going"
- Unique constraint per event/user

### Rating
- Event and User relationship
- 1-5 star rating system
- Optional feedback text
- Unique constraint per event/user

### Reminder Log
- Tracks sent email reminders
- Pre-event and post-event types

## Email Reminder System

The application includes an automated email reminder system using django-crontab:

- **Pre-event reminders**: Sent 2 days before event date
- **Post-event rating requests**: Sent 1 day after event date
- **Auto-complete events**: Optionally mark events as completed based on `auto_complete_datetime`

### Setup Cron Jobs (Production)
```bash
python manage.py crontab add
python manage.py crontab show
```

Recommended crontab entries (add in `settings.py` → `CRONJOBS`):

```python
CRONJOBS = [
    ('0 9 * * *', 'events.cron.send_event_reminders'),      # daily 09:00
    ('0 10 * * *', 'events.cron.send_rating_requests'),      # daily 10:00
    ('*/30 * * * *', 'events.cron.auto_complete_events'),    # every 30 minutes (optional)
]
```

### Manual Testing
```python
# In Django shell
from events.cron import send_event_reminders, send_rating_requests
send_event_reminders()
send_rating_requests()
```

### Auto-complete via Management Command
You can also run auto-completion as a one-off or from your own scheduler:

```bash
python manage.py auto_complete_events
```

## Configuration

### Email Settings (settings.py)
```python
# Development (console backend)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Production (SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

### Media Files
- Profile pictures: `media/profile_pics/`
- Event images: `media/event_pics/`
- Default images used by models: `media/default.jpg` (profile), `media/event_default.jpg` (events)

If these default files are missing, create simple placeholder images with those exact filenames in the `media/` directory to avoid file-not-found issues during image processing.

## API Endpoints

### Calendar Events API
- **URL**: `/api/calendar-events/`
- **Method**: GET
- **Response**: JSON array of all events for FullCalendar.js
- **Format**: 
  ```json
  [
    {
      "id": 1,
      "title": "Event Title",
      "start": "2024-01-15T19:00:00",
      "url": "/events/1/",
      "backgroundColor": "#FF7F50"
    }
  ]
  ```

### Key URLs
- `/` — Events list (search, filter, pagination)
- `/event/<id>/` — Event detail
- `/event/new/` — Create event
- `/event/<id>/update/` — Update event (creator only)
- `/event/<id>/delete/` — Delete event (creator only)
- `/event/<id>/rsvp/` — RSVP POST endpoint (login required)
- `/event/<id>/rate/` — Rate POST endpoint (login + attendee + past event)
- `/event/<id>/complete/` — Mark completed (creator only)
- `/event/<id>/undo-complete/` — Undo completed (creator only)
- `/completed/` — Completed events list
- `/my-rsvps/` — Your RSVPs (upcoming and past)

## Customization

### Color Scheme
The orange color scheme can be customized in `static/css/main.css`:
```css
:root {
    --orange-primary: #FF7F50;
    --orange-secondary: #FF8C42;
    --orange-light: #FFB347;
    --orange-lightest: #FFE5B4;
}
```

### Adding Features
1. Create new models in appropriate app
2. Add views and forms
3. Create templates
4. Update URL patterns
5. Run migrations

## Deployment

### Production Checklist
1. Set `DEBUG = False` in settings
2. Configure proper `ALLOWED_HOSTS`
3. Set up email backend (SMTP)
4. Configure static file serving
5. Set up media file serving
6. Configure database (PostgreSQL recommended)
7. Set up cron jobs for email reminders
8. Configure SSL certificate

### Deploying to Vercel
This project includes `vercel.json` configured to serve the Django app via `wsgi.py` with Python 3.12 runtime.

Notes:
- Vercel serverless functions do not run persistent background tasks. Use an external scheduler (e.g., GitHub Actions, GitLab CI, cron on a separate server) to trigger management commands or rely on request-time tasks only.
- Static files: collect locally during build and serve via a CDN or use WhiteNoise if deploying to a traditional server.
- Media uploads on serverless providers are ephemeral. Use an external storage service (e.g., S3, Cloudinary) for production.

### Environment Variables
Use python-decouple for environment-specific settings:
```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
```

## Browser Support
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Technologies Used
- **Backend**: Django 5.2.5, Python 3.10+ (tested with 3.12)
- **Frontend**: Bootstrap 5.3, HTML5, CSS3, JavaScript ES6
- **Database**: SQLite (development), PostgreSQL (production)
- **Calendar**: FullCalendar.js 6.1.8
- **Icons**: Font Awesome 6.0
- **Fonts**: Google Fonts (Poppins, Inter)
- **Image Processing**: Pillow
- **Forms**: django-crispy-forms with Bootstrap 5

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Submit a pull request

## License
This project is for educational purposes. Feel free to use and modify as needed.

## Support
For issues and questions, please create an issue in the repository or contact the development team.
