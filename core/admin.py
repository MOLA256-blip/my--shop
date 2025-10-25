from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, Transaction, Order, OrderItem, MobileMoneyPayment

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('city', 'state', 'address', 'phone', 'country', 'age', 'avatar')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'city', 'state', 'address', 'phone', 'is_staff', 'is_active'),

        }),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'user', 'amount', 'currency', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['transaction_id', 'user__username']
    readonly_fields = ['transaction_id', 'created_at', 'updated_at']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_image', 'quantity', 'unit_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'id']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderItemInline]


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
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('user', 'order', 'cart_code', 'provider', 'amount')
        }),
        ('Transaction Details', {
            'fields': ('phone_number', 'transaction_id', 'status')
        }),
        ('Verification', {
            'fields': ('created_at', 'verified_at', 'verified_by', 'notes')
        }),
    )
    
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
        """Verify selected payments"""
        count = 0
        for payment in queryset.filter(status='pending'):
            payment.verify(admin_user=request.user)
            count += 1
        
        self.message_user(
            request, 
            f'{count} payment(s) verified successfully',
            level='success'
        )
    verify_payments.short_description = '✅ Verify selected payments'
    
    def reject_payments(self, request, queryset):
        """Reject selected payments"""
        count = queryset.filter(status='pending').update(
            status='rejected',
            notes='Rejected by admin'
        )
        
        self.message_user(
            request, 
            f'{count} payment(s) rejected',
            level='warning'
        )
    reject_payments.short_description = '❌ Reject selected payments'
    
    def get_queryset(self, request):
        """Optimize queries"""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'order', 'verified_by')