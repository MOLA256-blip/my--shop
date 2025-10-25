"""
INSTRUCTIONS: Add this code to your core/models.py file

Copy the MobileMoneyPayment class below and paste it at the end of your models.py file
"""

# ============================================
# ADD THIS TO core/models.py
# ============================================

class MobileMoneyPayment(models.Model):
    """
    Model to track mobile money payments that need manual verification
    """
    PROVIDER_CHOICES = [
        ('mtn', 'MTN Mobile Money'),
        ('airtel', 'Airtel Money'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='mobile_payments')
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='mobile_payment')
    cart_code = models.CharField(max_length=100)
    provider = models.CharField(max_length=10, choices=PROVIDER_CHOICES)
    phone_number = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_payments')
    notes = models.TextField(blank=True, help_text='Admin notes about this payment')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mobile Money Payment'
        verbose_name_plural = 'Mobile Money Payments'
    
    def __str__(self):
        return f"{self.get_provider_display()} - {self.transaction_id} - {self.get_status_display()}"
    
    def verify(self, admin_user=None):
        """Mark payment as verified"""
        from django.utils import timezone
        self.status = 'verified'
        self.verified_at = timezone.now()
        if admin_user:
            self.verified_by = admin_user
        self.save()
        
        # Update order status
        if self.order:
            self.order.status = 'completed'
            self.order.save()
    
    def reject(self, reason=''):
        """Mark payment as rejected"""
        self.status = 'rejected'
        if reason:
            self.notes = reason
        self.save()
