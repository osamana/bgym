from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

from django.utils.translation import gettext_lazy as _


class Gym(models.Model):
    name = models.CharField(_('name'), max_length=100)
    address = models.TextField(_('address'))
    phone = models.CharField(_('phone'), max_length=15, blank=True, null=True)
    email = models.EmailField(_('email'), blank=True, null=True)

    def __str__(self):
        return self.name

    def total_clients(self):
        return Client.objects.filter(gym=self).count()

    def total_income(self):
        return Transaction.objects.filter(transaction_type='income', client__gym=self).aggregate(total=models.Sum('amount'))['total'] or 0

    def total_expenses(self):
        return Transaction.objects.filter(transaction_type='expense', client__gym=self).aggregate(total=models.Sum('amount'))['total'] or 0

    def balance(self):
        return self.total_income() - self.total_expenses()


class Client(models.Model):
    name = models.CharField(_('name'), max_length=100)
    phone = models.CharField(_('phone'), max_length=15, blank=True, null=True)
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def membership_status(self):
        now = timezone.now().date()
        active_memberships = self.membership_set.filter(end_date__gte=now)
        if not active_memberships.exists():
            return _("expired")

        soon_expiring_memberships = active_memberships.filter(end_date__lte=now + timedelta(days=7))
        if soon_expiring_memberships.exists():
            return _("expiring_soon")

        return _("active")

    def total_expenses(self):
        return self.transaction_set.filter(transaction_type='expense').aggregate(total=models.Sum('amount'))['total'] or 0

    def total_income(self):
        return self.transaction_set.filter(transaction_type='income').aggregate(total=models.Sum('amount'))['total'] or 0

    def balance(self):
        return self.total_income() - self.total_expenses()


class MembershipType(models.Model):
    name = models.CharField(_('name'), max_length=100)
    duration_months = models.PositiveIntegerField(_('duration in months'))
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

    def num_clients(self):
        return Membership.objects.filter(membership_type=self).count()


class Membership(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    membership_type = models.ForeignKey(MembershipType, on_delete=models.CASCADE)
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))

    def __str__(self):
        return f'{self.client} - {self.membership_type}'

    def is_active(self):
        now = timezone.now().date()
        return self.start_date <= now <= self.end_date

    def days_remaining(self):
        now = timezone.now().date()
        if self.is_active():
            return (self.end_date - now).days
        return 0


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', _('Income')),
        ('expense', _('Expense')),
    ]

    transaction_type = models.CharField(_('transaction type'), max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    date = models.DateField(_('date'))
    description = models.TextField(_('description'), blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
