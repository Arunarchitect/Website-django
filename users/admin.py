from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserAccount

class UserAccountAdmin(UserAdmin):
    model = UserAccount
    list_display = ('id','email', 'first_name', 'last_name', 'is_active', 'is_staff')  # Remove username, date_joined
    list_filter = ('is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')  # Search by email, first_name, and last_name
    ordering = ('email',)

    # Modify the fieldsets to exclude fields that do not exist in UserAccount
    fieldsets = (
        (None, {'fields': ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser')}),
        ('Permissions', {'fields': ('groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_active', 'is_staff')}),
    )

admin.site.register(UserAccount, UserAccountAdmin)
