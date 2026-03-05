from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_password_reset_email(reset_link, recipient_email):
    send_mail(
        subject='TaskFlow Password Reset',
        message=f'Click the link to reset your password: {reset_link}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_email],
    )


@shared_task
def send_due_date_reminders():
    from datetime import date, timedelta
    from tasks.models import Task
    tomorrow = date.today() + timedelta(days=1)
    tasks = Task.objects.filter(due_date=tomorrow, status__in=['pending', 'in_progress'])
    for task in tasks:
        send_mail(
            subject=f'TaskFlow Reminder: "{task.title}" is due tomorrow',
            message=f'Your task "{task.title}" is due tomorrow. Log in to complete it.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[task.owner.email],
        )