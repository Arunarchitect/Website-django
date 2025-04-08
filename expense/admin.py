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
    search_fields = (
        'item__name', 'category__name', 'brand__name',
        'shop__name', 'who_spent__username', 'remarks'
    )
    list_filter = ('category', 'brand', 'shop', 'unit', 'date_of_purchase')
    ordering = ('-date_of_purchase',)
