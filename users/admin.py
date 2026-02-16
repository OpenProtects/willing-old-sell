from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Notification


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['id', 'username', 'phone', 'real_name', 'credit_score', 
                    'is_verified', 'is_admin', 'is_active', 'date_joined']
    list_filter = ['is_verified', 'is_admin', 'is_active', 'face_verified']
    search_fields = ['username', 'phone', 'real_name', 'school_id']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('额外信息', {
            'fields': ('phone', 'real_name', 'id_card', 'avatar', 'credit_score',
                       'is_verified', 'face_verified', 'school_id', 'is_admin')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('额外信息', {
            'fields': ('phone', 'real_name', 'credit_score', 'is_verified', 'is_admin')
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
    search_fields = ['user__username', 'title']
    ordering = ['-created_at']
    raw_id_fields = ['user']
