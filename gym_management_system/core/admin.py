from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Client, MembershipType, Membership, Transaction, Gym
from django.urls import path
from django.shortcuts import render
from django.db.models import Count, Sum
from .forms import MembershipForm
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


class MembershipInline(admin.StackedInline):
    model = Membership
    extra = 0


class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "gym", "last_membership_day", "membership_status_indicator")
    search_fields = ("name", "phone")
    inlines = [MembershipInline]

    def membership_status_indicator(self, obj):
        status, status_label = obj.membership_status()
        if status == "no_membership":
            return format_html('<span style="color: red; font-size:2em;">&#x25CF;</span>')
        if status == "expired":
            return format_html('<span style="color: red; font-size:2em;">&#x25CF;</span>')
        elif status == "expiring_soon":
            return format_html('<span style="color: yellow; font-size:2em;">&#x25CF;</span>')
        else:
            return format_html('<span style="color: green; font-size:2em;">&#x25CF;</span>')

    membership_status_indicator.short_description = _("Membership Status")

    def last_membership_day(self, obj):
        return obj.last_membership_day()

    last_membership_day.short_description = _("Last Membership Day")

    class Media:
        js = ("js/client_admin.js",)


class MembershipTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "duration_months", "price")


class MembershipAdmin(admin.ModelAdmin):
    list_display = ("client", "membership_type", "formatted_start_date", "formatted_end_date")
    list_filter = ("client", "membership_type", "start_date", "end_date")
    search_fields = ("client__name", "membership_type__name")

    def formatted_start_date(self, obj):
        formatted_date = obj.start_date.strftime("%-d-%-m-%Y")
        return formatted_date

    formatted_start_date.admin_order_field = "start_date"
    formatted_start_date.short_description = _("Start Date")

    def formatted_end_date(self, obj):
        formatted_date = obj.end_date.strftime("%-d-%-m-%Y")
        return formatted_date

    formatted_end_date.admin_order_field = "end_date"
    formatted_end_date.short_description = _("End Date")

    form = MembershipForm

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if form.cleaned_data["add_income_transaction"]:
            Transaction.objects.create(
                transaction_type="income",
                client=obj.client,
                amount=obj.membership_type.price,
                date=obj.start_date,
                description=_("Income for {0} membership of {1}").format(obj.membership_type, obj.client),
            )


class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_icon",
        "transaction_type",
        "amount",
        "formatted_date",
        "description",
        "related_client",
    )
    list_filter = ("transaction_type", "date")
    search_fields = ("description",)

    def formatted_date(self, obj):
        formatted_date = obj.date.strftime("%-d-%-m-%Y")
        return formatted_date

    formatted_date.admin_order_field = "date"
    formatted_date.short_description = _("Date")

    def transaction_icon(self, obj):
        if obj.transaction_type == "income":
            return format_html('<span style="color: green; font-size: 2em;">&#x2B;</span>')  # Green plus icon
        elif obj.transaction_type == "expense":
            return format_html('<span style="color: red; font-size: 2em;">&#x2212;</span>')  # Red minus icon
        return ""

    transaction_icon.short_description = _("Icon")

    def related_client(self, obj):
        if obj.client:
            url = reverse("admin:core_client_change", args=[obj.client.id])
            return format_html('<a href="{}">{}</a>', url, obj.client)
        return None

    related_client.short_description = _("Related Client")


class GymAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "phone", "email", "total_clients", "total_income", "total_expenses", "balance")

    def total_income(self, obj):
        return obj.total_income()

    total_income.short_description = _("Total Income")

    def total_clients(self, obj):
        return obj.total_clients()

    total_clients.short_description = _("Total Clients")

    def total_expenses(self, obj):
        return obj.total_expenses()

    total_expenses.short_description = _("Total expenses")

    def balance(self, obj):
        return obj.balance()

    balance.short_description = _("Balance")

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("statistics/", self.admin_site.admin_view(self.statistics_view), name="gym-statistics"),
        ]
        return my_urls + urls

    def statistics_view(self, request):
        gyms = Gym.objects.annotate(
            total_clients=Count("client"),
            total_income=Sum(
                "client__transaction__amount", filter=models.Q(client__transaction__transaction_type="income")
            ),
            total_expenses=Sum(
                "client__transaction__amount", filter=models.Q(client__transaction__transaction_type="expense")
            ),
        )

        context = {
            "gyms": gyms,
            "title": _("Gym Statistics"),
        }
        return render(request, "core/admin/gym_statistics.html", context)


admin.site.register(Gym, GymAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(MembershipType, MembershipTypeAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(Transaction, TransactionAdmin)
