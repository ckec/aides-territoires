"""This is the "send email alerts upon new saved search results" feature."""

from datetime import timedelta
import logging

from django.utils import timezone
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.db.models import Q, Case, When
from django.urls import reverse
from django.conf import settings

from alerts.models import Alert


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Send an email alert upon new aid results."""

    def handle(self, *args, **options):

        alerts = self.get_alerts()
        alerted_alerts = []
        for alert in alerts:
            new_aids = list(alert.get_new_aids())
            if new_aids:
                alerted_alerts.append(alert.token)
                self.send_alert(alert, new_aids)
                logger.info(
                    'Sending alert alert email to {}: {} alerts'.format(
                        alert.email,
                        len(new_aids)))

        updated = Alert.objects \
            .filter(token__in=alerted_alerts) \
            .update(latest_alert_date=timezone.now())
        self.stdout.write('{} alerts sent'.format(updated))
        return

    def get_alerts(self):
        """Get alerts that could request a new email.

        Only return alerts with a latest alert date old enough to send
        a new one.
        """

        # Get the two date thresholds (daily and weekly alerts)
        now = timezone.now()
        yesterday = now - timedelta(days=1)
        last_week = now - timedelta(days=7)

        # Create the alert date query condition
        F = Alert.FREQUENCIES
        latest_alert_is_old_enough = Q(latest_alert_date__lte=Case(
            When(alert_frequency=F.daily, then=yesterday),
            When(alert_frequency=F.weekly, then=last_week)
        ))

        alerts = Alert.objects \
            .filter(validated=True) \
            .filter(
                Q(latest_alert_date__isnull=True) |
                latest_alert_is_old_enough)

        return alerts

    def send_alert(self, alert, new_aids):
        """Send an email alert with a summary of the newly published aids."""

        delete_url = reverse('alert_delete_view', args=[alert.token])
        site = Site.objects.get_current()
        email_context = {
            'domain': site.domain,
            'alert': alert,
            'nb_aids': len(new_aids),
            'new_aids': new_aids[:3],
            'delete_url': delete_url,
            'contact_phone': settings.CONTACT_PHONE,
        }

        text_body = render_to_string(
            'alerts/alert_body.txt', email_context)
        html_body = render_to_string(
            'alerts/alert_body.html', email_context)
        email_subject = '{:%d/%m/%Y} — De nouvelles aides correspondent à ' \
                        'vos recherches'.format(timezone.now())
        email_from = settings.DEFAULT_FROM_EMAIL
        email_to = [alert.email]

        send_mail(
            '{}{}'.format(settings.EMAIL_SUBJECT_PREFIX, email_subject),
            text_body,
            email_from,
            email_to,
            html_message=html_body,
            fail_silently=False)
