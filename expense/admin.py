from django.contrib import admin
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils.translation import gettext_lazy as _
import datetime
from .models import Expense, Item, Category, Brand, Shop
from django.contrib.auth import get_user_model

User = get_user_model()

# Custom Month Filter
class MonthFilter(admin.SimpleListFilter):
    title = _('month')
    parameter_name = 'month'

    def lookups(self, request, model_admin):
        months = Expense.objects.dates('date_of_purchase', 'month', order='DESC')
        return [(month.strftime("%Y-%m"), month.strftime("%B %Y")) for month in months]

    def queryset(self, request, queryset):
        if self.value():
            year, month = self.value().split('-')
            return queryset.filter(
                date_of_purchase__year=year,
                date_of_purchase__month=month
            )
        return queryset

# Custom Category Filter
class CategoryFilter(admin.SimpleListFilter):
    title = _('category')
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        categories = Category.objects.all().order_by('name')
        return [(category.id, category.name) for category in categories]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category__id=self.value())
        return queryset

# Custom User Filter
class UserFilter(admin.SimpleListFilter):
    title = _('user')
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        users = User.objects.filter(expense__isnull=False).distinct().order_by('first_name')
        return [(user.id, f"{user.first_name} {user.last_name}") for user in users]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(who_spent__id=self.value())
        return queryset

# Admin for Expense
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'who_spent', 'item', 'category', 'brand', 'shop',
        'date_of_purchase', 'quantity', 'unit', 'price', 'rate', 'remarks'
    )
    readonly_fields = ('rate',)
    ordering = ('-date_of_purchase',)
    list_per_page = 50
    change_list_template = 'admin/expense/expense/change_list.html'
    list_filter = (MonthFilter, CategoryFilter, UserFilter)  # Added all filters here

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        try:
            qs = response.context_data['cl'].queryset

            # Get active filters
            active_month = request.GET.get('month', None)
            active_category = request.GET.get('category', None)
            active_user = request.GET.get('user', None)

            # GRAND TOTAL (userwise)
            grand_total_by_user = (
                qs.values('who_spent__first_name', 'who_spent__last_name')
                  .annotate(total=Sum('price'))
                  .order_by('who_spent__first_name', 'who_spent__last_name')
            )

            grand_total = sum(entry['total'] for entry in grand_total_by_user)

            # MONTHLY TOTAL (userwise)
            monthly_totals = (
                qs.annotate(month=TruncMonth('date_of_purchase'))
                  .values('month', 'who_spent__first_name', 'who_spent__last_name')
                  .annotate(total=Sum('price'))
                  .order_by('-month', 'who_spent__first_name', 'who_spent__last_name')
            )

            # Preparing monthly data
            monthly_summary_dict = {}
            for entry in monthly_totals:
                month = entry['month'].strftime('%b %Y')
                user = f"{entry['who_spent__first_name']} {entry['who_spent__last_name']}".strip()
                total = entry['total']
                monthly_summary_dict.setdefault(month, []).append(f"{user}: ₹{total:.2f}")

            # Add the total for each month
            monthly_totals_summary = []
            for month, user_totals in monthly_summary_dict.items():
                monthly_total = sum(float(total.split('₹')[1].strip()) for total in user_totals)
                monthly_summary = f"{month} → " + ", ".join(user_totals) + f" | Total: ₹{monthly_total:.2f}"
                monthly_totals_summary.append(monthly_summary)

            # HTML Table Layout for Monthly Summary
            table_content = f"""
                <h3>Monthly Summary</h3>
                <div style="margin-bottom: 10px;">
                    <strong>Active Filters:</strong>
                    {f"Month: {active_month}" if active_month else ""}
                    {f", Category: {Category.objects.get(id=active_category).name}" if active_category else ""}
                    {f", User: {User.objects.get(id=active_user).get_full_name()}" if active_user else ""}
                </div>
                <table style="width: 100%; border: 1px solid #ddd; border-collapse: collapse;">
                    <thead>
                        <tr>
                            <th>Month</th>
                            <th>Userwise Totals</th>
                            <th>Monthly Total</th>
                        </tr>
                    </thead>
                    <tbody>
            """

            # Add monthly breakdown data to table
            for month_summary in monthly_totals_summary:
                month = month_summary.split("→")[0].strip()
                user_totals = month_summary.split("→")[1].split("|")[0].strip()
                total = month_summary.split("|")[1].strip()
                table_content += f"""
                    <tr>
                        <td>{month}</td>
                        <td>{user_totals}</td>
                        <td>{total}</td>
                    </tr>
                """

            table_content += "</tbody></table>"

            # Add the Userwise Grand Total
            table_content += f"""
                <h3>Userwise Grand Total</h3>
                <table style="width: 100%; border: 1px solid #ddd; border-collapse: collapse;">
                    <thead>
                        <tr>
                            <th>User</th>
                            <th>Total Amount</th>
                        </tr>
                    </thead>
                    <tbody>
            """

            for entry in grand_total_by_user:
                table_content += f"""
                    <tr>
                        <td>{entry['who_spent__first_name']} {entry['who_spent__last_name']}</td>
                        <td>₹{entry['total']:.2f}</td>
                    </tr>
                """

            table_content += "</tbody></table>"

            # Add the Grand Total
            table_content += f"""
                <h3>Grand Total</h3>
                <table style="width: 100%; border: 1px solid #ddd; border-collapse: collapse;">
                    <thead>
                        <tr>
                            <th>Total</th>
                            <th>Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Grand Total</td>
                            <td>₹{grand_total:.2f}</td>
                        </tr>
                    </tbody>
                </table>
            """

            # Set the content as extra context
            response.context_data['title'] = "Expense Summary"
            response.context_data['extra_context'] = {'table_content': table_content}

        except (AttributeError, KeyError):
            pass

        return response

# Register all models
admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Item)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Shop)