# forms.py
from django import forms
from .models import Membership
from django.utils.translation import gettext as _


class MembershipForm(forms.ModelForm):
    add_income_transaction = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Add an income transaction for this new membership")
    )

    class Meta:
        model = Membership
        fields = '__all__'
