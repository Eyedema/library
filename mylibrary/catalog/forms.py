import datetime

from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(
        help_text="Enter a date between now and 4 weeks (default 3 weeks).",
        widget=forms.DateInput(
            attrs={
                'type': 'date',  # Enables native date picker
                'class': 'pl-12 block w-full rounded-lg border border-gray-300 bg-white py-3 pr-3 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 transition duration-200',
            }
        )
    )

    def clean_renewal_date(self):
        data = self.cleaned_data["renewal_date"]

        # Check if a date is not in the past.
        if data < datetime.date.today():
            raise ValidationError(_("Invalid date - renewal in past"))

        # Check if a date is in the allowed range (+4 weeks from today).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_("Invalid date - renewal more than 4 weeks ahead"))

        # Remember to always return the cleaned data.
        return data
