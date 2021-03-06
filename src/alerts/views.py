from django.views.generic import CreateView, DetailView, DeleteView
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.http import HttpResponseRedirect
from braces.views import MessageMixin

from alerts.tasks import send_alert_confirmation_email
from alerts.forms import AlertForm
from alerts.models import Alert


class AlertCreate(MessageMixin, CreateView):
    """Create a alert by saving a search view querystring."""

    http_method_names = ['post']
    form_class = AlertForm

    def form_valid(self, form):
        alert = form.save()
        send_alert_confirmation_email.delay(alert.email, alert.token)
        message = _('We just sent you an email to validate your alert.')
        self.messages.success(message)
        redirect_url = reverse('search_view')
        return HttpResponseRedirect('{}?{}'.format(
            redirect_url, alert.querystring))

    def form_invalid(self, form):
        msg = _('We could not create your alert because of those '
                'errors: {}').format(form.errors.as_text())
        self.messages.error(msg)
        redirect_url = reverse('search_view')
        querystring = form.cleaned_data.get('querystring', '')
        return HttpResponseRedirect('{}?{}'.format(redirect_url, querystring))


class AlertValidate(MessageMixin, DetailView):
    """Confirms that the alert email is valid."""

    model = Alert
    slug_field = 'token'
    slug_url_kwarg = 'token'
    context_object_name = 'alert'
    template_name = 'alerts/validate.html'

    def post(self, *args, **kwargs):
        """Validates the alert."""

        alert = self.get_object()
        if not alert.validated:
            alert.validate()
            alert.save()

        msg = _('You confirmed the alert creation.')
        self.messages.success(msg)

        redirect_url = '{}?{}'.format(
            reverse('search_view'),
            alert.querystring)
        return HttpResponseRedirect(redirect_url)


class AlertDelete(MessageMixin, DeleteView):
    """Alert deletion view.

    Since we don't require a login to create alert, no authentication is
    required to delete them either.

    If you know the secret alert token, we suppose you are the owner, thus
    you can delete it.
    """
    model = Alert
    slug_field = 'token'
    slug_url_kwarg = 'token'
    context_object_name = 'alert'
    template_name = 'alerts/confirm_delete.html'

    def get_success_url(self):
        url = '{}?{}'.format(
            reverse('search_view'),
            self.object.querystring)
        return url

    def delete(self, *args, **kwargs):
        res = super().delete(*args, **kwargs)
        self.messages.success(_('The alert was deleted.'))
        return res
