from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active', 'is_email_verified',)
    list_filter = ('email', 'is_staff', 'is_active', 'is_email_verified',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_email_verified',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    readonly_fields = ['is_email_verified', ]

    search_fields = ('email',)
    ordering = ('email',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['email', ]
        return self.readonly_fields


admin.site.register(CustomUser, CustomUserAdmin)
