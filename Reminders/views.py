from django.shortcuts import render
from .models import Reminder
from django.contrib import messages

def reminders(request):
    if not Reminder.objects.all():
        Reminder.objects.create(
            frequency='Daily',
            last_sent=None,
            run_until=None,
            status='Stopped'
        )
    return render(request, 'reminders.html', {'reminder': Reminder.objects.first()})


def resume_reminder(request):
    reminder = Reminder.objects.first()
    reminder.status = 'Running'
    reminder.run_until = None
    reminder.save()
    return render(request, 'reminders.html', {'reminder': reminder})


def change_stoppage_date(request):
    reminder = Reminder.objects.first()
    reminder.run_until = request.POST.get('stoppage_date')
    reminder.save()
    print(reminder.run_until)
    messages.success(request, 'Stoppage date changed successfully.')
    return render(request, 'reminders.html', {'reminder': reminder})


def pause_reminder(request):
    reminder = Reminder.objects.first()
    reminder.status = 'Paused'
    reminder.save()
    return render(request, 'reminders.html', {'reminder': reminder})