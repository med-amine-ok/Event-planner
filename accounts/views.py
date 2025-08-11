from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    my_events = request.user.created_events.order_by('date', 'time')

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'going_rsvp_count': request.user.rsvp_set.filter(status='going').count(),
        'my_events': my_events,
    }
    return render(request, 'accounts/profile.html', context)


def logout_view(request):
    """Allow logout via GET to support nav link."""
    if request.method in ['POST', 'GET']:
        logout(request)
        # Show confirmation page instead of redirecting
        return render(request, 'accounts/logout.html')
    return redirect('events-home')
