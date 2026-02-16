from django.contrib import admin
from .models import CreditRecord


@admin.register(CreditRecord)
class CreditRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'change_type', 'change_score', 'before_score', 
                    'after_score', 'reason', 'created_at']
    list_filter = ['change_type']
    search_fields = ['user__username', 'reason']
    raw_id_fields = ['user', 'operator']
    ordering = ['-created_at']
