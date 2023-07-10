from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from celery.schedules import crontab
from datetime import date

from backend_task import settings
from backend_task.celery import app as celery_app


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # Executes every day at 10:30 a.m.
    sender.add_periodic_task(
        crontab(hour=10, minute=30),
        send_birthday_email.s("<<<<<< Happy birthday to you!! >>>>>>>"),
    )


@celery_app.task
def send_birthday_email(msg):
    users = get_user_model().objects.exclude(
        email__isnull=True).exclude(email__exact='')
    today = date.today()
    for user in users:
        user_bday = user.birthday
        if not all((today.day == user_bday.day, today.month == user_bday.month)):
            continue
        mail_subject = f"Happy Birthday {user.username}"
        send_mail(
            subject=mail_subject,
            message=msg,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=True,
        )
    return "Birthday email was successfully sent!"
