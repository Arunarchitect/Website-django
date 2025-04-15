from django.contrib import admin
from django.db.models import Sum
from .models import Expense, Item, Category, Brand, Shop


class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'who_spent', 'item', 'category', 'brand', 'shop',
        'date_of_purchase', 'quantity', 'unit', 'price', 'rate', 'remarks'
    )
    readonly_fields = ('rate',)
    ordering = ('-date_of_purchase',)

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        try:
            qs = response.context_data['cl'].queryset
            total_price = qs.aggregate(total=Sum('price'))['total'] or 0
            response.context_data['title'] += f" (Total Price: ₹{total_price:.2f})"
        except (AttributeError, KeyError):
            pass
        return response


# Register all models properly
admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Item)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Shop)
