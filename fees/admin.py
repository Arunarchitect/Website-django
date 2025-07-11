# fees/admin.py

from django.contrib import admin
from .models import Fee, PromoCode

@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ('promo_code', 'base_fee_per_sqft', 'consultant', 'designation','url')
    
admin.site.register(PromoCode)
