// Event Planner - Main JavaScript File

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar functionality
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const navLinks = document.querySelectorAll('.nav-links a');
    

    
    // Toggle sidebar
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.add('active');
            sidebarOverlay.classList.add('active');
            document.body.classList.add('sidebar-open');
        });
    }
    
    // Close sidebar when overlay is clicked
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            closeSidebar();
        });
    }
    

    
    // Close sidebar when nav links are clicked (mobile)
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 991.98) {
                closeSidebar();
            }
        });
    });
    
    // Close sidebar on window resize (if screen becomes large)
    window.addEventListener('resize', function() {
        if (window.innerWidth > 991.98) {
            closeSidebar();
        }
    });
    
    // Close sidebar function
    function closeSidebar() {
        if (sidebar) {
            sidebar.classList.remove('active');
        }
        if (sidebarOverlay) {
            sidebarOverlay.classList.remove('active');
        }
        document.body.classList.remove('sidebar-open');
    }
    
    // Auto-hide alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 500);
        }, 5000);
    });
    
    // Animate cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe all cards
    const cards = document.querySelectorAll('.card, .event-card');
    cards.forEach(function(card) {
        observer.observe(card);
    });
    
    // RSVP Form Handler
    const rsvpForms = document.querySelectorAll('.rsvp-form');
    rsvpForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                submitBtn.disabled = true;
            }
        });
    });
    
    // Rating Form Handler
    const ratingForms = document.querySelectorAll('.rating-form');
    ratingForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
                submitBtn.disabled = true;
            }
        });
    });
    
    // Star Rating Interactive
    const starRatings = document.querySelectorAll('.star-rating');
    starRatings.forEach(function(rating) {
        const stars = rating.querySelectorAll('.star');
        const input = rating.querySelector('input[type="hidden"]');
        
        stars.forEach(function(star, index) {
            star.addEventListener('click', function() {
                const value = index + 1;
                input.value = value;
                updateStarDisplay(stars, value);
            });
            
            star.addEventListener('mouseover', function() {
                const value = index + 1;
                updateStarDisplay(stars, value);
            });
        });
        
        rating.addEventListener('mouseleave', function() {
            const value = input.value || 0;
            updateStarDisplay(stars, value);
        });
    });
    
    function updateStarDisplay(stars, value) {
        stars.forEach(function(star, index) {
            if (index < value) {
                star.classList.remove('far');
                star.classList.add('fas');
            } else {
                star.classList.remove('fas');
                star.classList.add('far');
            }
        });
    }
    
    // Search form auto-submit on filter change
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        const filterInputs = searchForm.querySelectorAll('input, select');
        filterInputs.forEach(function(input) {
            if (input.type !== 'submit') {
                input.addEventListener('change', function() {
                    searchForm.submit();
                });
            }
        });
    }
    
    // Countdown timer for events
    const countdownElements = document.querySelectorAll('.countdown-timer');
    countdownElements.forEach(function(element) {
        const eventDate = new Date(element.dataset.eventDate);
        
        function updateCountdown() {
            const now = new Date();
            const difference = eventDate - now;
            
            if (difference > 0) {
                const days = Math.floor(difference / (1000 * 60 * 60 * 24));
                const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((difference % (1000 * 60)) / 1000);
                
                element.innerHTML = `
                    <div class="countdown-item">
                        <span class="countdown-number">${days}</span>
                        <span class="countdown-label">Days</span>
                    </div>
                    <div class="countdown-item">
                        <span class="countdown-number">${hours}</span>
                        <span class="countdown-label">Hours</span>
                    </div>
                    <div class="countdown-item">
                        <span class="countdown-number">${minutes}</span>
                        <span class="countdown-label">Minutes</span>
                    </div>
                    <div class="countdown-item">
                        <span class="countdown-number">${seconds}</span>
                        <span class="countdown-label">Seconds</span>
                    </div>
                `;
            } else {
                element.innerHTML = '<span class="text-muted">Event has started!</span>';
            }
        }
        
        updateCountdown();
        setInterval(updateCountdown, 1000);
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Image preview for file inputs
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    let preview = input.parentNode.querySelector('.image-preview');
                    if (!preview) {
                        preview = document.createElement('div');
                        preview.className = 'image-preview mt-2';
                        input.parentNode.appendChild(preview);
                    }
                    
                    preview.innerHTML = `
                        <img src="${e.target.result}" alt="Preview" style="max-width: 200px; max-height: 200px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <p class="text-muted mt-1">${file.name}</p>
                    `;
                };
                reader.readAsDataURL(file);
            }
        });
    });
    
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                const firstInvalidField = form.querySelector('.is-invalid');
                if (firstInvalidField) {
                    firstInvalidField.focus();
                }
            }
        });
    });
});



// Calendar initialization function
function initializeCalendar() {
    const calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        const eventsUrl = calendarEl.getAttribute('data-events-url') || '/api/calendar-events/';
        const calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,listWeek'
            },
            events: eventsUrl,
            eventClick: function(info) {
                window.location.href = info.event.url;
            },
            eventMouseEnter: function(info) {
                info.el.style.transform = 'scale(1.05)';
                info.el.style.zIndex = '999';
            },
            eventMouseLeave: function(info) {
                info.el.style.transform = 'scale(1)';
                info.el.style.zIndex = 'auto';
            },
            height: 'auto',
            aspectRatio: 1.8,
            eventDisplay: 'block',
            dayMaxEvents: 3,
            moreLinkClick: 'popover',
            eventTimeFormat: {
                hour: 'numeric',
                minute: '2-digit',
                meridiem: 'short'
            }
        });
        
        calendar.render();
    }
}

// Copy to clipboard function
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        // Show success message
        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--orange-primary);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            z-index: 9999;
            animation: slideInRight 0.3s ease;
        `;
        toast.textContent = 'Copied to clipboard!';
        
        document.body.appendChild(toast);
        
        setTimeout(function() {
            toast.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(function() {
                toast.remove();
            }, 300);
        }, 2000);
    });
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .countdown-timer {
        display: flex;
        gap: 1rem;
        justify-content: center;
        align-items: center;
        background: linear-gradient(135deg, var(--orange-lightest), rgba(255, 179, 71, 0.3));
        padding: 1rem;
        border-radius: var(--border-radius);
        margin: 1rem 0;
    }
    
    .countdown-item {
        text-align: center;
        min-width: 60px;
    }
    
    .countdown-number {
        display: block;
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--orange-primary);
        font-family: 'Poppins', sans-serif;
    }
    
    .countdown-label {
        display: block;
        font-size: 0.8rem;
        color: var(--gray-medium);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
`;

document.head.appendChild(style);
