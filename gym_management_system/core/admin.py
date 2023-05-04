from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Client, MembershipType, Membership, Transaction, Gym
from django.urls import path
from django.shortcuts import render
from django.db.models import Count, Sum
from .forms import MembershipForm
from django.utils.html import format_html
from django.utils.translation import gettext as _


class MembershipInline(admin.StackedInline):
    model = Membership
    extra = 0


class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'gym', 'membership_status_indicator')
    inlines = [MembershipInline]

    def membership_status_indicator(self, obj):
        status = obj.membership_status()
        if status == 'expired':
            return format_html('<span style="color: red;">&#x25CF;</span>')
        elif status == 'expiring_soon':
            return format_html('<span style="color: yellow;">&#x25CF;</span>')
        else:
            return format_html('<span style="color: green;">&#x25CF;</span>')

    membership_status_indicator.short_description = _('Membership Status')


class MembershipTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_months', 'price')


class MembershipAdmin(admin.ModelAdmin):
    list_display = ('client', 'membership_type', 'start_date', 'end_date')
    list_filter = ('client', 'membership_type', 'start_date', 'end_date')
    search_fields = ('client__name', 'membership_type__name')

    form = MembershipForm

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if form.cleaned_data['add_income_transaction']:
            Transaction.objects.create(
                transaction_type='income',
                client=obj.client,
                amount=obj.membership_type.price,
                date=obj.start_date,
                description=_('Income for {0} membership of {1}').format(obj.membership_type, obj.client)
            )


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_icon', 'transaction_type', 'amount', 'date', 'description', 'related_client')
    list_filter = ('transaction_type', 'date')
    search_fields = ('description',)

    def transaction_icon(self, obj):
        if obj.transaction_type == 'income':
            return format_html('<span style="color: green;">&#x1F4B0;</span>')  # Green money bag emoji
        elif obj.transaction_type == 'expense':
            return format_html('<span style="color: red;">&#x1F4B8;</span>')  # Red money with wings emoji
        return ''

    transaction_icon.short_description = _('Icon')

    def related_client(self, obj):
        if obj.client:
            url = reverse('admin:core_client_change', args=[obj.client.id])
            return format_html('<a href="{}">{}</a>', url, obj.client)
        return None

    related_client.short_description = _('Related Client')


class GymAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'email', 'total_clients', 'total_income', 'total_expenses', 'balance')

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('statistics/', self.admin_site.admin_view(self.statistics_view), name='gym-statistics'),
        ]
        return my_urls + urls

    def statistics_view(self, request):
        gyms = Gym.objects.annotate(
            total_clients=Count('client'),
            total_income=Sum('client__transaction__amount', filter=models.Q(
                client__transaction__transaction_type='income')),
            total_expenses=Sum('client__transaction__amount', filter=models.Q(
                client__transaction__transaction_type='expense'))
        )

        context = {
            'gyms': gyms,
            'title': _('Gym Statistics'),
        }
        return render(request, 'core/admin/gym_statistics.html', context)


admin.site.register(Gym, GymAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(MembershipType, MembershipTypeAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(Transaction, TransactionAdmin)
