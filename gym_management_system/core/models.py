from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

from django.utils.translation import gettext_lazy as _


class Gym(models.Model):
    class Meta:
        verbose_name = _("gym")
        verbose_name_plural = _("gyms")

    name = models.CharField(_("name"), max_length=100)
    address = models.TextField(_("address"))
    phone = models.CharField(_("phone"), max_length=15, blank=True, null=True)
    email = models.EmailField(_("email"), blank=True, null=True)

    def __str__(self):
        return self.name

    def total_clients(self):
        return Client.objects.filter(gym=self).count()

    def total_income(self):
        return (
            Transaction.objects.filter(transaction_type="income", client__gym=self).aggregate(
                total=models.Sum("amount")
            )["total"]
            or 0
        )

    def total_expenses(self):
        return (
            Transaction.objects.filter(transaction_type="expense", client__gym=self).aggregate(
                total=models.Sum("amount")
            )["total"]
            or 0
        )

    def balance(self):
        return self.total_income() - self.total_expenses()


class Client(models.Model):
    class Meta:
        verbose_name = _("client")
        verbose_name_plural = _("clients")

    name = models.CharField(_("name"), max_length=100)
    phone = models.CharField(_("phone"), max_length=15, blank=True, null=True)
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, verbose_name=_("gym"))

    def __str__(self):
        return self.name

    def membership_status(self):
        now = timezone.now().date()
        if not self.membership_set.exists():
            return "no_membership", _("no_membership")
        active_memberships = self.membership_set.filter(end_date__gte=now)
        if not active_memberships.exists():
            return "expired", _("expired")

        soon_expiring_memberships = active_memberships.filter(end_date__lte=now + timedelta(days=7))
        if soon_expiring_memberships.exists():
            return "expiring_soon", _("expiring_soon")

        return "active", _("active")

    def total_expenses(self):
        return (
            self.transaction_set.filter(transaction_type="expense").aggregate(total=models.Sum("amount"))["total"] or 0
        )

    def total_income(self):
        return (
            self.transaction_set.filter(transaction_type="income").aggregate(total=models.Sum("amount"))["total"] or 0
        )

    def balance(self):
        return self.total_income() - self.total_expenses()

    # last day of active membership (if any)
    def last_membership_day(self):
        now = timezone.now().date()
        if self.membership_set.exists():
            active_memberships = self.membership_set.filter(end_date__gte=now)
            if active_memberships.exists():
                return active_memberships.latest("end_date").end_date.strftime("%-d-%-m-%Y")
        return None


class MembershipType(models.Model):
    class Meta:
        verbose_name = _("membership type")
        verbose_name_plural = _("membership types")

    name = models.CharField(_("name"), max_length=100)
    duration_months = models.PositiveIntegerField(_("duration in months"))
    price = models.DecimalField(_("price"), max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

    def num_clients(self):
        return Membership.objects.filter(membership_type=self).count()


class Membership(models.Model):
    class Meta:
        verbose_name = _("membership")
        verbose_name_plural = _("memberships")

    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name=_("client"))
    membership_type = models.ForeignKey(MembershipType, on_delete=models.CASCADE, verbose_name=_("membership type"))
    start_date = models.DateField(_("start date"))
    end_date = models.DateField(_("end date"))

    def __str__(self):
        return f"{self.client} - {self.membership_type}"

    def is_active(self):
        now = timezone.now().date()
        return self.start_date <= now <= self.end_date

    def days_remaining(self):
        now = timezone.now().date()
        if self.is_active():
            return (self.end_date - now).days
        return 0


class Transaction(models.Model):
    class Meta:
        verbose_name = _("transaction")
        verbose_name_plural = _("transactions")

    TRANSACTION_TYPES = [
        ("income", _("Income")),
        ("expense", _("Expense")),
    ]

    transaction_type = models.CharField(_("transaction type"), max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(_("amount"), max_digits=10, decimal_places=2)
    date = models.DateField(_("date"))
    description = models.TextField(_("description"), blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
