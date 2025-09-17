from django.contrib import admin

# Register your models here.
from .models import wallet, contact_request, withdraw_request, Trade, Deposit





admin.site.register(wallet)
admin.site.register(Trade)
admin.site.register(contact_request)
admin.site.register(withdraw_request)

@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('user', 'coin', 'amount', 'wallet_address', 'created_at')
    list_filter = ('coin', 'created_at')
    search_fields = ('user__username', 'coin', 'wallet_address')

from .models import Deposit, Withdrawal

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('user', 'coin', 'amount', 'wallet_address', 'status', 'created_at')
    list_filter = ('coin', 'status', 'created_at')
    search_fields = ('user__username', 'coin', 'wallet_address')