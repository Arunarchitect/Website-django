from django.contrib import admin
from .models import Expense, Item, Category, Brand, Shop

admin.site.register(Item)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Shop)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'who_spent', 'item', 'category', 'brand', 'shop',
        'date_of_purchase', 'quantity', 'unit', 'price', 'rate', 'remarks'
    )
    readonly_fields = ('rate',)
    # search_fields = (...)  # Temporarily comment out
    # list_filter = (...)    # Temporarily comment out
    ordering = ('-date_of_purchase',)
