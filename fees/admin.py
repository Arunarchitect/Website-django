# fees/admin.py

from django.contrib import admin
from .models import Fee, PromoCode

admin.site.register(Fee)
admin.site.register(PromoCode)
