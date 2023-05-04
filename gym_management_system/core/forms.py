# forms.py
from django import forms
from .models import Membership

class MembershipForm(forms.ModelForm):
    add_income_transaction = forms.BooleanField(
        required=False,
        initial=True,
        label="Add an income transaction for this new membership"
    )

    class Meta:
        model = Membership
        fields = '__all__'
