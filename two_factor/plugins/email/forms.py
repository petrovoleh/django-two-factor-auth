from django import forms
from django.utils.translation import gettext_lazy as _

from two_factor.forms import (
    AuthenticationTokenForm as BaseAuthenticationTokenForm,
    DeviceValidationForm as BaseValidationForm,
)


class EmailForm(forms.Form):
    email = forms.EmailField(label=_("Email address"))

    def __init__(self, **kwargs):
        kwargs.pop('device', None)
        super().__init__(**kwargs)


class DeviceValidationForm(forms.Form):
    token = forms.CharField(label=_("Token"))
    
    # Add attributes to the widget
    token.widget.attrs.update({
        'autofocus': 'autofocus',
        'autocomplete': 'one-time-code'
    })
    
    idempotent = False  # Token is not reusable once validated

    def __init__(self, device, *args, **kwargs):
        super().__init__(**kwargs)
        self.device = device

    def clean_token(self):
        """
        Validates the token and ensures it's correct for the device.
        """
        token = self.cleaned_data['token']
        if not self.device.verify_token(token):
            raise forms.ValidationError(_("The provided token is invalid."))
        return token

    def save(self):
        """
        Marks the device as confirmed and saves it.

        :param commit: Whether to save the device to the database.
        :return: The updated device instance.
        """
        self.device.confirmed = True
        self.device.save()
        return self.device



class AuthenticationTokenForm(BaseAuthenticationTokenForm):
    def _chosen_device(self, user):
        return self.initial_device
