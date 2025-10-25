"""
INSTRUCTIONS: Update your core/admin.py file

Add this import at the top:
"""

from .mobile_money_models import MobileMoneyPayment
from django.utils.html import format_html

"""
Then add this admin class:
"""

@admin.register(MobileMoneyPayment)
class MobileMoneyPaymentAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 
        'provider_badge', 
        'user',
        'phone_number', 
        'amount_display',
        'status_badge', 
        'created_at',
        'order'
    ]
    list_filter = ['status', 'provider', 'created_at']
    search_fields = ['transaction_id', 'phone_number', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'verified_at', 'verified_by']
    
    actions = ['verify_payments', 'reject_payments']
    
    def provider_badge(self, obj):
        colors = {'mtn': '#FFCC00', 'airtel': '#E60000'}
        color = colors.get(obj.provider, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_provider_display()
        )
    provider_badge.short_description = 'Provider'
    
    def status_badge(self, obj):
        colors = {'pending': '#ffc107', 'verified': '#28a745', 'rejected': '#dc3545'}
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def amount_display(self, obj):
        return format_html('<strong>₦{:,.2f}</strong>', obj.amount)
    amount_display.short_description = 'Amount'
    
    def verify_payments(self, request, queryset):
        count = 0
        for payment in queryset.filter(status='pending'):
            payment.verify(admin_user=request.user)
            count += 1
        self.message_user(request, f'{count} payment(s) verified', level='success')
    verify_payments.short_description = '✅ Verify selected payments'
    
    def reject_payments(self, request, queryset):
        count = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{count} payment(s) rejected', level='warning')
    reject_payments.short_description = '❌ Reject selected payments'
